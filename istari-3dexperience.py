import json
import os
import random
import tempfile
from io import BytesIO
from mcp.server.fastmcp import FastMCP
from PIL import Image

from shared.constants import *
from shared.helpers import *


mcp = FastMCP("istari-mcp-server")


@mcp.tool()
def get_3dx_parameters(model_id: str) -> str:
  """Retrieves parameters for a 3DExperience/3DX/CATIA model with the specified model ID.

     Args:
       model_id (str): A string containing the ID of the model for which parameters will be retrieved.
  """
  try:
    req_data = download_artifact_data(model_id,
                                      PARAM_FILE_NAME)
    ret_str = req_data.decode('utf-8')
  except FileNotFoundError:
    ret_str = 'Parameters artifact not found. Extract parameters from the 3DX model first.'

  return ret_str


@mcp.tool()
def get_3dx_components(model_id: str) -> str:
  """Retrieves information about components such as:
     * Material
     * Center of gravity
     * Bounding box dimensions
     * Mass
     * Area
     * Volume
  
     Args:
       model_id (str): A string containing the ID of the model for which parameters will be retrieved.
  """
  try:
    req_data = download_artifact_data(model_id,
                                      PARTS_FILE_NAME)
    ret_str = req_data.decode('utf-8')
  except FileNotFoundError:
    ret_str = 'Components artifact not found. Extract artifacts from the 3DExperience model first.'

  return ret_str


@mcp.tool()
def extract_3dx_model_artifacts(model_id: str) -> str:
  """Extracts artifacts from a 3DExperience/3DX/CATIA model with the specified ID.

     Args:
       model_id (str): A string containing the ID of the model for which parameters will be retrieved.
  """
  print('Submitting job to extract 3DX model requirements ...')

  job = submit_job(model_id = model_id,
                   function = '@istari:extract',
                   tool_name = CAD_TOOL_NAME)
  print(f"Job submitted with ID: {job.id}")

  job = wait_for_job(job)
  return f"Job Complete [{job.status.name}]"


@mcp.tool()
def extract_3dx_model_parameters(model_id: str,
                                 full_extract: bool) -> str:
  """Extracts parameters from a 3DExperience/3DX/CATIA model with the specified ID.

     Args:
       model_id (str): A string containing the ID of the model for which parameters will be retrieved.
       full_extract (bool): If True, all model parameters will be extracted. Otherwise, only user parameters will be extracted.
  """
  print('Submitting job to extract 3DX model requirements ...')

  input_file = 'input.json'
  with open(input_file, 'w') as fout:
    fout.write(f"{{\"full_extract\": {str(full_extract).lower()}}}")

  job = submit_job(model_id = model_id,
                   function = '@istari:extract_parameters',
                   tool_name = CAD_TOOL_NAME,
                   params_file = input_file)
  print(f"Job submitted with ID: {job.id}")

  os.remove(input_file)
  job = wait_for_job(job)
  return f"Job Complete [{job.status.name}]"


@mcp.tool()
def update_3dx_model_parameters(model_id: str,
                                params: dict[str, str]) -> None:
  """Updates parameters in the specified 3DExperience/3DX/CATIA model with the specified ID.

     Args:
       model_id (str): A string containing the ID of the model for which parameters will be retrieved.
       params (dict[str, str]): A dictionary containing keys with the parameter names and values with the desired parameter value.  Parameter values should include units. Actual parameter names must be used.
  """
  print ('Submitting job to update 3DX model parameters ...')

  #params = params.replace('\\', '\\\\')
  input_json = {'parameters': params} #json.loads(params)}
  input_file = 'input.json'
  with open(input_file, 'w') as fout:
    json.dump(input_json,
              fout)

  job = submit_job(model_id = model_id,
                   function = '@istari:update_parameters',
                   tool_name = CAD_TOOL_NAME,
                   params_file = input_file)
  print(f"Job submitted with ID: {job.id}")

  os.remove(input_file)
  job = wait_for_job(job)

  client = get_client()
  mod = client.get_model(model_id);
  with open(mod.name, 'wb') as fout:
    fout.write(mod.file.revisions[0].read_bytes())

  client.update_model(model_id,
                      mod.name)

  return f"Job Complete [{job.status.name}]"


@mcp.tool()
def view_3dx_model(model_id: str,
                   view: str) -> str:
  """Displays images of various views of a 3DExperience/3DX model.

     Args:
       model_id (str): A string containing the ID of the model for which parameters will be retrieved.
       view (str): A string specifying the desired view of the model. Options are: 
         * front
         * back
         * left
         * right
         * top
         * bottom
         * iso
  """

  ret_str = 'Image has been displayed'
  try:
    art_name = f"{view}_view.bmp"
    img_data = download_artifact_data(model_id,
                                      art_name)
    byte_data = BytesIO(img_data)
    img = Image.open(byte_data)
    img.show()
  except FileNotFoundError:
    ret_str = 'Image artifact not found. Extract artifacts from the 3DX model first.'
    
  return ret_str


if __name__ == "__main__":
  print("MCP Server is running")
  mcp.run(transport='stdio')
