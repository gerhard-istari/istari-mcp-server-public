import json
import logging
import os
import random
import tempfile
from io import BytesIO
from mcp.server.fastmcp import FastMCP
from PIL import Image
from pydantic import Json

from shared.constants import *
from shared.helpers import *
from iterators.cameo_requirements_iterator import CameoRequirementsIterator


mcp = FastMCP("istari-mcp-server")

logging.getLogger('openai').setLevel(logging.ERROR)
logging.getLogger('httpx').setLevel(logging.ERROR)


@mcp.tool()
def get_cameo_requirements(model_id: str) -> str:
  """Retrieves requirements for Cameo model with the specified model ID.

     Args:
       model_id (str): A string containing the ID of the model for which parameters will be retrieved.
  """
  try:
    req_data = download_artifact_data(model_id,
                                      REQ_FILE_NAME)
    ret_str = req_data.decode('utf-8')
  except FileNotFoundError:
    ret_str = 'Requirements artifact not found. Extract the requirements from the cameo model first.'

  return ret_str


@mcp.tool()
def extract_cameo_model_artifacts(model_id: str) -> str:
  """Extracts artifacts from a Cameo model with the specified ID.

     Args:
       model_id (str): A string containing the ID of the model for which parameters will be retrieved.
  """
  print('Submitting job to extract Cameo model requirements ...')
  job = submit_job(model_id = model_id,
                   function = '@istari:extract',
                   tool_name = CAMEO_TOOL_NAME,
                   tool_ver = CAMEO_VERSION)
  print(f"Job submitted with ID: {job.id}")

  job = wait_for_job(job)
  return f"Job Complete [{job.status.name}]"


@mcp.tool()
async def search_cameo_model_requirements(model_id: str,
                                          query: str) -> list[Json]:
  """Iterates through all model requirements and finds any relevant to the
     submitted query.

     Args:
       model_id (str): The ID of the Cameo model containing the requirements
       query (str): The query string

     Returns:
       A list of dictionaries containing requirements metadata.
  """
  with open('C:/Users/n8440g/Downloads/requirements.json', 'r') as fin:
    reqs_json = json.load(fin)

  cameo_iter = CameoRequirementsIterator(reqs_json)
  print('Searching requirements')
  matches = await search_artifact_data(query,
                                       cameo_iter)
  print('Search complete')
  print(f"Found {len(matches)} matching requirements")
  return matches


if __name__ == "__main__":
  print("MCP Server is running")
  mcp.run(transport='stdio')
