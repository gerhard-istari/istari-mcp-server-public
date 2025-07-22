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
def get_named_cells(model_id: str) -> str:
  """Retrieves information about all of the named cells in an Excel model, including:
     * The sheet name on which the named cell is located
     * The row and column of the named cell in a "Range" parameter
     * The value of the named cell

     Args:
       model_id (str): A string containing the ID of the model from which named cells will be retrieved.
  """
  try:
    nc_data = download_artifact_data(model_id,
                                     NAMED_CELLS_FILE_NAME)
    ret_str = nc_data.decode('utf-8')
  except FileNotFoundError:
    ret_str = 'Named cells artifact not found. Extract named cells from the Excel model first.'

  return ret_str


@mcp.tool()
def extract_named_cells(model_id: str) -> str:
  """Extracts the named cells artifact from an Excel model.

     Args:
       model_id (str): A string containing the ID of the model from which the named cells will be extracted.
  """

  job = submit_job(model_id = model_id,
                   function = '@istari:extract',
                   tool_name = EXCEL_TOOL_NAME)
  print(f"Job submitted with ID: {job.id}")

  job = wait_for_job(job)
  return f"Job Complete [{job.status.name}]"


@mcp.tool()
def update_cell_value(model_id: str,
                      sheet_name: str,
                      row_index: int,
                      column_index: int,
                      cell_value: str) -> str:
  """Updates the value of a cell with the specified name with the specified value in an Excel model.
     Note that the row and column indices must first be retrieved for named cells.

     Args:
       model_id (str): A string containing the ID of the model for which the named cell will be updated.
       sheet_name (str): The name of the sheet containing the cell to update.
       row_index (str): The 1-based index of the row of the cell to be updated.
       column_index (str): The 1-based index of the column of the cell to be updated.
       cell_value (str): The updated value of the cell.
  """
  input_json = {"sheet_name": sheet_name,
                "row": row_index,
                "column": column_index,
                "new_cell_value": cell_value}

  input_file = 'input.json'
  with open(input_file, 'w') as fout:
    json.dump(input_json,
              fout)

  job = submit_job(model_id = model_id,
                   function = '@istari:update_cell',
                   tool_name = EXCEL_TOOL_NAME,
                   params_file = input_file)
  print(f"Job submitted with ID: {job.id}")

  os.remove(input_file)
  job = wait_for_job(job)
  
  if str(job.status.name).find('COMPLETE') >= 0:
    client = get_client()
    excl_mod_name = get_model_display_name(model_id)
    excl_file = os.path.join(tempfile.gettempdir(),
                             f"{excl_mod_name}.xlsx")
    download_artifact(model_id,
                      MOD_WB_FILE_NAME,
                      excl_file)
    try: # BUG: This throws an exception for some reason
      client.update_model(model_id,
                          excl_file)
    except Exception as excp:
      return f"Exception thrown: {excp}"

    os.remove(excl_file)

  return f"Job Complete [{job.status.name}]"


if __name__ == "__main__":
  print("MCP Server is running")
  mcp.run(transport='stdio')
