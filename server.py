import os
import random
from mcp.server.fastmcp import FastMCP

from shared.constants import *
from shared.helpers import *


mcp = FastMCP("istari-mcp-server")

@mcp.tool()
def get_model_ids() -> list[str]:
  """Gets the names and IDs of all available models.

     Returns:
       A list of strings containing the model names and IDs separated by a '|' character.
  """
  client = get_client()
  pg_idx = 1
  mod_pg = client.list_models(pg_idx)

  mods = []
  while len(mod_pg.items) > 0:
    for mod_itm in mod_pg.items:
      mod_id = mod_itm.id
      mod_rev = mod_itm.file.revisions[-1]
      mods.append(f"{mod_rev.name} | {mod_id}")

    pg_idx += 1
    mod_pg = client.list_models(pg_idx)

  return mods


@mcp.tool()
def get_cameo_requirements(model_id: str) -> str:
  """Retrieves requirements for Cameo model with the specified model ID.

     Args:
       mod_id (str): The ID of the model for which requirements should be retrieved.
  """
  try:
    req_data = download_artifact_data(model_id,
                                      REQ_FILE_NAME)
    ret_str = req_data.decode('utf-8')
  except FileNotFoundError:
    ret_str = 'Requirements artifact not found. Extract the requirements from the cameo model first.'

  return ret_str


@mcp.tool()
def get_3dx_parameters(model_id: str) -> str:
  """Retrieves parameters for a 3DExperience/3DX/CATIA model with the specified model ID.

     Args:
       mod_id (str): The ID of the model for which parameters should be retrieved.
  """
  try:
    req_data = download_artifact_data(model_id,
                                      PARAM_FILE_NAME)
    ret_str = req_data.decode('utf-8')
  except FileNotFoundError:
    ret_str = 'Requirements artifact not found. Extract the requirements from the cameo model first.'

  return ret_str


@mcp.tool()
def get_3dx_components(model_id: str) -> str:
  """Retrieves information about components such as:
     * Materials
     * Center of gravity
     * Bounding box dimensions
  
     Args:
       mod_id (str): The ID of the model for which parameters should be retrieved.
  """
  try:
    req_data = download_artifact_data(model_id,
                                      PARTS_FILE_NAME)
    ret_str = req_data.decode('utf-8')
  except FileNotFoundError:
    ret_str = 'Components artifact not found. Extract the component from the 3DExperience model first.'

  return ret_str


@mcp.tool()
def extract_cameo_model_artifacts(model_id: str) -> str:
  """Extracts artifacts from a Cameo model with the specified ID.

     Args:
       mod_id (str): The ID of the model for which artifacts should be extracted.
  """
  print('Submitting job to extract Cameo model requirements ...')
  job = submit_job(model_id = model_id,
                   function = '@istari:extract',
                   tool_name = CAMEO_TOOL_NAME,
                   tool_ver = CAMEO_VERSION)
  print(f"Job submitted with ID: {job.id}")

  wait_for_job(job)
  return f"Job Complete [{job.status.name}]"


@mcp.tool()
def extract_3dx_model_artifacts(model_id: str,
                                full_extract: bool) -> str:
  """Extracts artifacts from a 3DExperience/3DX/CATIA model with the specified ID.

     Args:
       mod_id (str): The ID of the model for which artifacts should be extracted.
       full_extract (bool): If True, all model parameters will be extracted. Otherwise, only user parameters will be extracted.
  """
  print('Submitting job to extract 3DX model requirements ...')

  input_file = 'input.json'
  with open(input_file, 'w') as fout:
    fout.write(f"{{\"full_extract\": {str(full_extract).lower()}}}")

  job = submit_job(model_id = model_id,
                   function = '@istari:extract',
                   tool_name = CAD_TOOL_NAME,
                   params_file = input_file)
  print(f"Job submitted with ID: {job.id}")

  wait_for_job(job)
  return f"Job Complete [{job.status.name}]"


if __name__ == "__main__":
    print("MCP Server is running")
    mcp.run(transport='stdio')
