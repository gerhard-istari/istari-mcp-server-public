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
def get_nastran_results(model_id: str) -> str:
  """Retrieves Nastran simulation results data such as:
     * Displacements (Translations/Rotations)
     * Accelerations
     * Forces
     * Stresses

     Args:
       model_id (str): The UUID of the Nastran model
  """
  try:
    data = download_artifact_data(model_id,
                                  OP2_SUMMARY_FILE_NAME)
    ret_str = data.decode('utf-8')
  except FileNotFoundError:
    ret_str = 'Nastran result summary artifact not found. Extract the results artifact first.'

  return ret_str


@mcp.tool()
def get_material_data(model_id: str) -> str:
  """Retrieves Nastran model material data.

     Args:
       model_id (str): The UUID of the Nastran model
  """
  try:
    data = download_artifact_data(model_id,
                                  MAT_SUMMARY_FILE_NAME)
    ret_str = data.decode('utf-8')
  except FileNotFoundError:
    ret_str = 'Nastran material summary artifact not found. Extract the materials artifact first.'

  return ret_str


@mcp.tool()
def extract_nastran_input(model_id: str) -> str:
  """Extracts information from a Nastran input (bdf) file.

     Args:
       model_id (str): The UUID of the Nastran bdf model to extract
  """
  job = submit_job(model_id = model_id,
                   function = '@istari:extract_input',
                   tool_name = NASTRAN_EXTRACT_TOOL_NAME)
  print(f"Job submitted with ID: {job.id}")

  job = wait_for_job(job)
  return f"Job Complete [{job.status.name}]"


@mcp.tool()
def extract_nastran_results(model_id: str) -> str:
  """Extracts information from a Nastran output (op2) file.

     Args:
       model_id (str): The UUID of the Nastran bdf model to extract
  """
  nast_res_file = os.path.join(tempfile.gettempdir(),
                               NASTRAN_RESULTS_FILE_NAME)
  try:
    download_artifact(model_id,
                      NASTRAN_RESULTS_FILE_NAME,
                      nast_res_file)
  except FileNotFoundError:
    return 'Nastran results artifact not found. Execute the Nastran model first.'

  client = get_client()
  op2_mod = client.add_model(nast_res_file)
  
  job = submit_job(model_id = op2_mod.id,
                   function = '@istari:extract_results',
                   tool_name = NASTRAN_EXTRACT_TOOL_NAME)
  print(f"Job submitted with ID: {job.id}")

  os.remove(nast_res_file)
  job = wait_for_job(job)

  if str(job.status.name).find('COMPLETE') >= 0:
    op2_summ_file = os.path.join(tempfile.gettempdir(),
                                 OP2_SUMMARY_FILE_NAME)
    download_artifact(op2_mod.id,
                      OP2_SUMMARY_FILE_NAME,
                      op2_summ_file)
    client.add_artifact(model_id,
                        op2_summ_file)
    os.remove(op2_summ_file)
    client.archive_model(op2_mod.id)

  return f"Job Complete [{job.status.name}]"
                      

@mcp.tool()
def execute_nastran_simulation(model_id: str) -> str:
  """Executes a Nastran simulation on the specified model.

     Args:
       model_id (str): The UUID of the Nastran model
  """
  job = submit_job(model_id = model_id,
                   function = '@istari:run',
                   tool_name = NASTRAN_TOOL_NAME)
  print(f"Job submitted with ID: {job.id}")

  job = wait_for_job(job)
  return f"Job Complete [{job.status.name}]"


if __name__ == "__main__":
  print("MCP Server is running")
  mcp.run(transport='stdio')
