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
def get_model_ids() -> dict[str, dict[str, str]]:
  """Gets the UUIDs and associated metadata of all available models.

     Returns:
       A dictionary with model UUIDs as keys and various model metadata in the values.
  """
  client = get_client()
  pg_idx = 1
  mod_pg = client.list_models(pg_idx)

  mods = {}
  while len(mod_pg.items) > 0:
    for mod_itm in mod_pg.items:
      mod_id = mod_itm.id
      mod_rev = mod_itm.file.revisions[-1]
      mods[mod_id] = {"name": mod_rev.name,
                      "display_name": mod_rev.display_name,
                      "revision_id": str(mod_rev.id),
                      "creation_date": str(mod_rev.created),
                      "extension": mod_rev.extension,
                      "size": mod_rev.size,
                      "sources": str(mod_rev.sources)}


    pg_idx += 1
    mod_pg = client.list_models(pg_idx)

  return mods


@mcp.tool()
def list_model_artifacts(model_id: str) -> dict[str, dict[str, str]]:
  """Gets the UUIDs and associated metadata of all artifacts for a given model UUID.

     Args:
       model_id (str): A string containing the UUID of the model.

     Returns:
       A dictionary with artifact UUIDs as keys and various artifact metadata in the values.
  """
  client = get_client()
  mod = client.get_model(model_id)
  mod_rev = mod.file.revisions[-1]

  arts = {}
  pg_idx = 1
  while True:
    art_list = client.list_model_artifacts(model_id,
                                           page = pg_idx)
    art_items = art_list.items
    if len(art_items) == 0:
      break
    
    for art_itm in art_items:
      art_rev = art_itm.file.revisions[-1]
      for art_rev_src in art_rev.sources:
        if mod_rev.id == art_rev_src.revision_id:
          arts[art_itm.id] = {"name": art_itm.name,
                              "display_name": art_rev.display_name,
                              "revision_id": str(art_rev.id),
                              "creation_date": str(art_rev.created),
                              "extension": art_rev.extension,
                              "size": art_rev.size,
                              "sources": str(art_rev.sources)}

    pg_idx += 1

  return arts


@mcp.tool()
def get_model_artifact(model_id: str,
                       artifact_name: str) -> bytes:
  return download_artifact_data(model_id,
                                artifact_name)


@mcp.tool()
def view_artifact(model_id: str,
                  artifact_name: str) -> str:
  """Displays an image artifact for the specified model.

     Args:
       model_id (str): A string containing the UUID of the model containing the artifact to view.
       artifact_name (str): The name of the artifact to view.
  """

  try:
    art_bytes = download_artifact_data(model_id,
                                       artifact_name)
    byte_data = BytesIO(art_bytes)
    img = Image.open(byte_data)
    img.show()
    ret_str = 'Image displayed successfully'
  except FileNotFoundError:
    ret_str = 'Image artifact not found. Extract artifacts from the model first.'

  return ret_str


@mcp.tool()
def update_model(model_id: str,
                 model_file: str) -> str:
  """Updates a model with a new version from the specified file.

     Args:
       model_id (str): A string containing the ID of the model to update.
       model_file (str): The name of the file to upload as a new version of the model.
  """
  client = get_client()
  disp_name,_ = os.path.splitext(os.path.basename(model_file))
  client.update_model(model_id,
                      model_file,
                      display_name=disp_name)

  return 'Model updated successfully'


@mcp.tool()
def upload_model(model_file: str,
                 model_id: str = None) -> str:
  """Pushes/Uploads a file to Istari as a new model or as an updated version.

     Args:
       model_file (str): The path to the file to upload.
       model_id (str): To update an existing model, this should be the model ID. Leave blank to upload as a new model.
  """
  client = get_client()
  if model_id is None or model_id == '':
    mod = client.add_model(model_file)
  else:
    mod = client.update_model(model_id,
                              model_file)

  return f"Model uploaded with UUID: {mod.id}"


if __name__ == "__main__":
  print("MCP Server is running")
  mcp.run(transport='stdio')
  #download_artifact('ccca4eb8-9634-4542-a983-5cc07db8e559',
  #                  'modified_workbook.xlsx',
  #                  'mod_wb.xlsx')
