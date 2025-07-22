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



if __name__ == "__main__":
  print("MCP Server is running")
  mcp.run(transport='stdio')

