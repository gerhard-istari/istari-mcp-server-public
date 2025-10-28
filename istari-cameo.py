import json
import logging
#import multiprocessing
import os
import random
import sys
import tempfile

from io import BytesIO
from mcp.server.fastmcp import FastMCP
from PIL import Image
from pydantic import Json
from typing import Optional

from istari_digital_client import NewSource, FunctionAuthType

from shared.constants import *
from shared.helpers import *


mcp = FastMCP("istari-mcp-server")
twc_auth_src = None

logging.getLogger('openai').setLevel(logging.ERROR)
logging.getLogger('httpx').setLevel(logging.ERROR)


def get_twc_auth_src(model_id: str) -> list[NewSource]:
  global twc_auth_src
  client = get_client()
  mod = client.get_model(model_id)
  mod_name, mod_ext = os.path.splitext(mod.name)

  if mod_ext.lower() != '.mdzip' and twc_auth_src is None:
    print("Generating TWC Auth")
    twc_auth_json = "twc_auth.json"
    if not os.path.exists(twc_auth_json):
      raise FileNotFoundError(f"Missing TWC authorization file: {twc_auth_json}")

    secret = client.add_function_auth_secret(path = twc_auth_json,
                                             function_auth_type = FunctionAuthType.BASIC)
    twc_auth_src = [NewSource(revision_id = secret.revision.id,
                              relationship_identifier = 'twc_auth_login')]
  return twc_auth_src


def get_full_func_name(func_name: str,
                       auth_src: list[NewSource] = None) -> str:
  return f"@istari:{'twc_' if auth_src else ''}{func_name}"


@mcp.tool()
def extract_cameo_model_artifacts(model_id: str) -> str:
  """Extracts artifacts from a Cameo model with the specified ID.

     Args:
       model_id (str): A string containing the ID of the model to extract artifacts.
  """
  if isinstance(model_id, dict):
    return extract_cameo_model_artifacts(**model_id)

  print('Submitting job to extract Cameo model requirements ...')
  twc_auth_src = get_twc_auth_src(model_id)
  func_name = get_full_func_name('extract',
                                 twc_auth_src)
  job = submit_job(model_id = model_id,
                   function = func_name,
                   tool_name = CAMEO_TOOL_NAME,
                   tool_ver = CAMEO_VERSION,
                   sources = twc_auth_src)
  print(f"Job submitted with ID: {job.id}")

  job = wait_for_job(job)
  return f"Job Complete [{job.status.name}]"


@mcp.tool()
async def get_cameo_model_requirements(model_id: str,
                                       query: Optional[list[str]] = None) -> str:
  """Retrieves requirements for a Cameo model with the specified model ID.
     If a query string is specified, iterates through all model requirements 
     and returns those relevant to the submitted query.

     Args:
       model_id (str): The ID of the Cameo model containing the requirements.
       query (list[str]): A list of query strings. If any queries are a match,
       the requirement will be returned. If empty or omitted, returns all
       requirements.

     Returns:
       A list of dictionaries containing requirements metadata.
  """
  if isinstance(model_id, dict):
    return await get_cameo_model_requirements(**model_id)

  reqs_json = []
  try:
    reqs_data = download_artifact_data(model_id,
                                       REQ_FILE_NAME)
    reqs_str = reqs_data.decode('windows-1252')
    reqs_json = json.loads(reqs_str)
  except FileNotFoundError:
    return 'Artifact not found. Extract the artifacts from the cameo model first.'

  if query and len(query):
    #cameo_iter = ArrayIterator(reqs_json)
    print('Searching requirements')
    matches = await search_artifact_data(query,
                                         reqs_json.__iter__(),
                                         batch_group_count = 100,
                                         max_iter_delay = 0.001)
    print('Search complete')
    print(f"Requirements Matches: {len(matches)}")
  else:
    matches = reqs_json

  return json.dumps(matches)


@mcp.tool()
def update_element_tags(model_id: str,
                        elem_tags: dict[str, dict[str, str]]) -> str:
  """Updates the element tags/attributes within the specified Cameo model.

     Args:
       model_id (str): The ID of the Cameo model to update.
       elem_tags (Json): A dictionary containing information about the element
       attributes to update. This dictionary should contain the element IDs as
       keys and dictionaries with attribute names and values as the values, as
       demonstrated in the following example:
       {
         "elem_id1": {
           "attr_name1": "attr_val1",
           "attr_name2": "attr_val2"
         },
         "elem_id2": {
           "attr_name1": "attr_val1",
           "attr_name2": "attr_val2",
           "attr_name3": "attr_val3"
         }
       }
  """
  elems_json = []
  for elem_name in elem_tags:
    update_json = {
      'element_id': elem_name,
      'tags': elem_tags[elem_name]
    }
    elems_json.append(update_json)
  updates_json = {'updates': elems_json}
    
  input_file = os.path.join(tempfile.gettempdir(),
                            'input_json.txt')
  with open(input_file, 'w') as fout:
    fout.write(json.dumps(updates_json))

  try:
    twc_auth_src = get_twc_auth_src(model_id)
    func_name = get_full_func_name('update_tags',
                                   twc_auth_src)
    job = submit_job(model_id = model_id,
                     function = func_name,
                     tool_name = CAMEO_TOOL_NAME,
                     tool_ver = CAMEO_VERSION,
                     params_file = input_file,
                     sources = twc_auth_src)
    print(f"Job submitted with ID: {job.id}")
  finally:
    os.remove(input_file)

  job = wait_for_job(job)

  return f"Job Complete [{job.status.name}]"


if __name__ == "__main__":
  #multiprocessing.freeze_support()
  print("MCP Server is running")
  mcp.run(transport='stdio')

  #print(extract_cameo_model_artifacts("10427dac-55c7-4f64-881e-2622a458a13a"))
  #print(asyncio.run(get_cameo_model_requirements({
  #    "model_id": "c0ae5fe3-2072-449a-b1f3-987009cb0ffd", #"5897eeb5-5ddf-402d-ac57-baf94a28cd68", #"c0ae5fe3-2072-449a-b1f3-987009cb0ffd",
  #      "query": [
  #          "vertical speed"
  #          #"environmental control system"
  #                ]
  #})))
  #print(update_element_tags(
  #  "c645f73e-4419-492a-bcc2-c1c6d5e50805",
  #  {"_2024x_2_72001a6_1759162498700_487331_429": {
  #                "Verification Document Paragraph": "Page 11, Paragraph 2",
  #                      "Verification Status": "Passed"
  #                          }}))
