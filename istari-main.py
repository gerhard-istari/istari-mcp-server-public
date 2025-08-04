import json
import os
import random
import tempfile
from io import BytesIO
from mcp.server.fastmcp import FastMCP
from PIL import Image
from istari_digital_client.models import NewSnapshot, NewSystem, NewSystemConfiguration, NewTrackedFile, AccessRelationship, AccessRelation, AccessSubjectType, AccessResourceType
from istari_digital_client.models.tracked_file_specifier_type import TrackedFileSpecifierType

from shared.constants import *
from shared.helpers import *


mcp = FastMCP("istari-mcp-server")

@mcp.tool()
def get_models() -> dict[str, dict[str, str]]:
  """Gets the UUIDs and associated metadata of all available models.

     Returns:
       A dictionary with keys containing model UUIDs and values containing model metadata.
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
def get_users() -> dict[str, dict[str, str]]:
  """Gets the UUIDs and associated metadata of all users.

     Returns:
       A dictionary with keys containing user UUIDs and values containing user metadata.
  """
  client = get_client()
  users = client.list_users()
  user_list = {}
  for user in users:
    user_list[user.id] = {"user_name": user.user_name,
                          "user_type": str(user.user_type),
                          "display_name": user.display_name,
                          "first_name": user.first_name,
                          "last_name": user.last_name,
                          "email": user.email}

  return user_list


@mcp.tool()
def get_systems() -> dict[str, dict[str, str]]:
  """Gets the UUIDs and associated metadata of all available systems.

     Returns:
       A dictionary with keys containing system UUIDs and values containing system metadata.
  """
  client = get_client()
  pg_idx = 1
  sys_pg = client.list_systems(pg_idx)

  systems = {}
  while len(sys_pg.items) > 0:
    for sys_itm in sys_pg.items:
      sys_id = sys_itm.id
      systems[sys_id] = {"name": sys_itm.name,
                         "description": sys_itm.description,
                         "creation_date": str(sys_itm.created)}

    pg_idx += 1
    sys_pg = client.list_systems(pg_idx)

  return systems


@mcp.tool()
def share_resource_with_user(resource_id: str,
                             user_id: str,
                             access_type: str,
                             resource_type: str) -> str:
  """Shares a resource with a specified user. The resource may be a model, artifact or system.

     Args:
       resource_id (str): A string containing the UUID of the resource to share.
       user_id (str): A string containing the UUID of the user with who to share the model.
       access_type (str): A string indicating the level of access provided to the model. Valid values are:
          * 'Viewer'
          * 'Editor'
          * 'Owner'
          * 'Administrator'
       resource_type (str): A string indicating what type of resource should be shared. Valid values are:
          * 'Model'
          * 'Artifact'
          * 'System'
  """
  share_object(resource_id,
               user_id,
               access_type,
               resource_type)
  return 'Resource shared successfully'


@mcp.tool()
def get_model_artifacts(model_id: str) -> dict[str, dict[str, str]]:
  """Gets the UUIDs and associated metadata of all artifacts produced by a specified model.

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
def get_system_model_ids(system_id: str,
                         snapshot_id: str = None) -> list[str]:
  """Gets the UUIDs of all models contained in a specified system.

     Args:
       system_id (str): A string specifying the UUID of the system.
       snapshot_id (str): If specified, the UUID of the snapshot to search for model IDs, otherwise the baseline snapshot is used.

     Returns:
       A list of model UUIDs contained by the system.
  """
  client = get_client()
  sys = client.get_system(system_id)

  model_ids = []
  pg_idx = 1
  snpsht_pg = sys.list_file_revisions_by_snapshot(page=pg_idx)
  while len(snpsht_pg.items) > 0:
    for snpsht_itm in snpsht_pg.items:
      file = client.get_file(snpsht_itm.file_id)
      if file.resource_type == 'Model':
        model_ids.append(file.resource_id)

    pg_idx += 1
    snpsht_pg = sys.list_file_revisions_by_snapshot(page=pg_idx)

  return model_ids


@mcp.tool()
def get_system_snapshots(system_id: str) -> dict[str, dict[str, str]]:
  """Gets the snapshots associated with a specified system.

     Args:
       system_id (str): A string specifying the UUID of the system.

     Returns:
       A dictionary with the snapshot UUIDs as keys and the values containing snapshot metadata.
  """
  client = get_client()
  sys = client.get_system(system_id)

  sys_snpshts = {}
  pg_idx = 1
  snpsht_pg = client.list_snapshots(system_id,
                                    page=pg_idx)
  while len(snpsht_pg.items) > 0:
    for snpsht_sys in snpsht_pg.items:
      snpsht_mods = {}
      snpsht_arts = {}
      snpsht_mod_pg_idx = 1
      snpsht_mod_pg = client.list_snapshot_items(snpsht_sys.id,
                                                 snpsht_mod_pg_idx)
      while len(snpsht_mod_pg.items) > 0:
        for snpsht_itm in snpsht_mod_pg.items:
          snpsht_itm_rev_id = snpsht_itm.file_revision_id
          snpsht_file = client.get_file_by_revision_id(snpsht_itm_rev_id)
          if snpsht_file.resource_type == "Model":
            snpsht_mods[snpsht_file.resource_id] = snpsht_itm_rev_id

        snpsht_mod_pg_idx += 1
        snpsht_mod_pg = client.list_snapshot_items(snpsht_sys.id,
                                                   snpsht_mod_pg_idx)

      user_name = client.get_user_by_id(snpsht_sys.created_by_id).display_name
      sys_snpshts[snpsht_sys.id] = {"creation_date": str(snpsht_sys.created),
                                    "created_by": user_name,
                                    "model_revisions": snpsht_mods}

    pg_idx += 1
    snpsht_pg = client.list_snapshots(system_id,
                                      page=pg_idx)

  return sys_snpshts


@mcp.tool()
def get_system_configurations(system_id: str) -> dict[str, dict[str, str]]:
  """Gets the configurations associated with a specified system.

     Args:
       system_id (str): A string specifying the UUID of the system.

     Returns:
       A dictionary with the configuration UUIDs as keys and the values containing configuration metadata.
  """
  client = get_client()
  sys = client.get_system(system_id)
  cfgs = {}

  for sys_cfg in sys.configurations:
    user_name = client.get_user_by_id(sys_cfg.created_by_id).display_name
    cfgs[sys_cfg.id] = {"name": sys_cfg.name,
                        "creation_date": sys_cfg.created,
                        "created_by": user_name}

  return cfgs


@mcp.tool()
def create_system(name: str,
                  description: str,
                  model_ids: list[str] = None) -> str:
  """Creates a new system with the specified models.

     Args:
       name (str): The name of the system to be created.
       description (str): A description for the newly created system.
       model_ids (list[str]): A list of model UUIDs to add to the new system. If None, an empty system will be created.
    
     Returns:
       The UUID of the newly created system.
  """
  client = get_client()
  new_sys = NewSystem(name=name,
                      description=description)
  sys = client.create_system(new_sys)
  files = []
  if not model_ids == None and len(model_ids) > 0:
    for model_id in model_ids:
      mod = client.get_model(model_id)
      files.append(NewTrackedFile(specifier_type=TrackedFileSpecifierType.LATEST,
                                  file_id=mod.file.id))

  new_cfg = NewSystemConfiguration(name='Default Configuration',
                                   tracked_files=files)
  client.create_configuration(sys.id,
                              new_cfg)

  return str(sys.id)


@mcp.tool()
def create_system_snapshot(system_id: str) -> str:
  """Creates a snapshot for the specified system.

     Args:
       system_id (str): The UUID of the system to add a snapshot to.
  """
  client = get_client()
  sys = client.get_system(system_id)
  cfg_id = sys.configurations[-1].id

  new_snpsht = NewSnapshot()
  client.create_snapshot(cfg_id,
                         new_snpsht)
  return 'System snapshot created successfully'


@mcp.tool()
def create_system_configuration(system_id: str,
                                config_name: str,
                                model_ids: list[str]) -> str:
  """Creates a new configuration in a system with the specified models.

     Args:
       system_id (str): The UUID of the system to create the new configuration in.
       config_name (str): The name of the configuration to be created.
       model_ids (list[str]): A list of model UUIDs to add to the new system. If None, an empty configuration will be created.
    
     Returns:
       The UUID of the newly created configuration.
  """
  client = get_client()
  files = []
  if not model_ids == None and len(model_ids) > 0:
    for model_id in model_ids:
      mod = client.get_model(model_id)
      files.append(NewTrackedFile(specifier_type=TrackedFileSpecifierType.LATEST,
                                  file_id=mod.file.id))

  new_cfg = NewSystemConfiguration(name=config_name,
                                   tracked_files=files)
  cfg = client.create_configuration(system_id,
                                    new_cfg)
  return str(cfg.id)


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


def share_object(obj_id: str,
                 user_id: str,
                 access_type: str,
                 resource_type: str) -> None:
  client = get_client()

  access_type = access_type.lower()
  access = None
  if access_type == 'viewer': access = AccessRelation.VIEWER
  elif access_type == 'editor': access = AccessRelation.EDITOR
  elif access_type == 'owner': access = AccessRelation.OWNER
  elif access_type == 'administrator': access = AccessRelation.ADMINISTRATOR
  else: raise SyntaxError(f"Invalid access level specified: {access}")

  resource_type = resource_type.lower()
  resource = None
  if resource_type == 'model': resource = AccessResourceType.MODEL
  elif resource_type == 'artifact': resource = AccessResourceType.ARTIFACT
  elif resource_type == 'system': resource = AccessResourceType.SYSTEM
  else: raise SyntaxError(f"Invalid resource type specified: {resource_type}")

  ar = AccessRelationship(subject_type=AccessSubjectType.USER,
                          subject_id=user_id,
                          relation=access,
                          resource_type=resource,
                          resource_id=obj_id)
  client.create_access(ar)


if __name__ == "__main__":
  print("MCP Server is running")
  mcp.run(transport='stdio')
