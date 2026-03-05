"""
This MCP server executes gitlab pipelines given a configuration json file that
is detailed in the README.
"""
import json
import os
import requests
import sys
import tempfile
import threading
import time
import urllib.parse

from datetime import datetime
from mcp.server.fastmcp import FastMCP
from pydantic import Json
from typing import Any

from istari_digital_client import Client

from shared.constants import *
from shared.helpers import *


VAR_MOD_NAME = 'VARIABLES_MODEL_ID'
mcp = FastMCP("istari-gitlab-server")

dotenv_file = 'gitlab.env'
if is_executable():
  dotenv_file = os.path.join(os.path.dirname(sys.executable),
                             dotenv_file)

dotenv.load_dotenv(dotenv_path=dotenv_file,
                   override=True)


def get_model_info(client: Client,
                   mod_data: dict[str, dict[str, str]],
                   config_dir: str) -> dict[str, str]:
  mod_info = {}
  for mod_name, mod_metadata in mod_data.items():
    mod_type = mod_metadata['type']
    if mod_type == 'path':
      mod_path = mod_metadata['value']
      if not os.path.isabs(mod_path):
        mod_path = os.path.join(config_dir,
                                mod_path)

      if not os.path.exists(mod_path):
        raise FileNotFoundError(f"Model not found: {mod_path}")

      print(f"Uploading model {mod_path} ...")
      mod = client.add_model(mod_path)
      print(f"Model uploaded with ID: {mod.id}")
    else:
      mod = client.get_model(mod_metadata['value'])

    mod_info[mod_name] = {'id': mod.id,
                          'rev_id': mod.file.revision.id,
                          'name': mod.name}

  return mod_info


def upload_var_data(client: Client,
                    var_data: dict[str, str],
                    var_mod_id: str = None) -> str:
  var_file = os.path.join(tempfile.gettempdir(),
                          'variables.json')
  with open(var_file, 'w') as fout:
    json.dump(var_data, fout, indent=2)

  if var_mod_id is None:
    print('Uploading variables file ...')
    var_mod = client.add_model(var_file)
    var_mod_id = var_mod.id
    print(f"Variables file uploaded with ID: {var_mod.id}")
  else:
    print('Updating variables file ...')
    client.update_model(var_mod_id,
                        var_file)

  os.remove(var_file)
  return var_mod_id


def exec_pipeline(mod_info: dict[str, str],
                  inp_var_dicts: list[dict[str, dict[str, str]]],
                  cfg_data: dict[str, Any],
                  cfg_dir: str,
                  bail_on_fail: bool = True) -> None:

  client = get_client()

  var_data = cfg_data['input_variables']
  if VAR_MOD_NAME in mod_info.keys():
    var_mod_id = mod_info[VAR_MOD_NAME]['id']
  else:
    var_mod_id = upload_var_data(client,
                                 var_data)

  infos = []
  for inp_vars in inp_var_dicts:
    # Create working directory
    now = datetime.now()
    work_dir = os.path.join(cfg_data['results_directory'],
                            now.strftime('%m-%d-%Y_%H%M%S'))
    if not os.path.isabs(work_dir):
      work_dir = os.path.join(cfg_dir,
                              work_dir)
    os.makedirs(work_dir)

    # Get pipeline token file
    cfg_pl_data = cfg_data['pipeline']
    pipeline_token_file = cfg_pl_data['token_file']
    if not os.path.isabs(pipeline_token_file):
      pipeline_token_file = os.path.join(cfg_dir,
                                         pipeline_token_file)

    # Variables
    if not inp_vars is None:
      for var_name in inp_vars:
        var_data[var_name] = inp_vars[var_name]

    upload_var_data(client,
                    var_data,
                    var_mod_id)

    pipeline_data = trigger_pipeline(cfg_pl_data['gitlab_url'],
                                     pipeline_token_file,
                                     cfg_pl_data['branch'],
                                     cfg_pl_data['project_id'],
                                     cfg_pl_data['workflow'],
                                     mod_info,
                                     var_mod_id)

    # Write workflow info to results dir
    info = {}
    infos.append(info)
    info['results_directory'] = work_dir

    pl_info = info['pipeline'] = {}
    pl_info['gitlab_url'] = cfg_pl_data['gitlab_url']
    for key in ['branch', 'project_id', 'workflow']:
      pl_info[key] = cfg_pl_data[key]

    pl_info['id'] = pipeline_data['id']
    pl_info['submit_time'] = pipeline_data['created_at']
    pipeline_user = pipeline_data['user']
    pl_info['user'] = {'username': pipeline_user['username'],
                       'name': pipeline_user['name']}

    info['models'] = mod_info
    info['input_variables'] = var_data

    iter_info_file = os.path.join(work_dir,
                                  'workflow_info.json')
    with open(iter_info_file, 'w') as fout:
      json.dump(info, fout, indent=2)

    # Wait for pipeline completion before proceeding
    pl_stat = wait_for_pipeline(pl_info)
    status = pl_stat.get('status', 'Unknown')
    if bail_on_fail and not status == 'success':
      print(f"Pipeline execution was not successful: {status}")
      break

    info['status'] = status
    with open(iter_info_file, 'w') as fout:
      json.dump(info, fout, indent=2)

  # Cleanup
  client.archive_model(var_mod_id)


def trigger_pipeline(gitlab_url: str,
                     token_file: str,
                     branch: str,
                     project_id: str,
                     workflow: str,
                     mod_info: dict[str, Json],
                     var_mod_id: str) -> dict[str, str]:
  payload = {}
  payload['ref'] = branch
  payload['variables[WORKFLOW]'] = workflow
  payload[f"variables[{VAR_MOD_NAME}]"] = var_mod_id
  payload['variables[REG_URL]'] = os.environ['REG_URL']
  payload['variables[REG_AUTH_TOKEN]'] = os.environ['REG_AUTH_TOKEN']

  for var_name, mod_data in mod_info.items():
    payload[f"variables[{var_name}]"] = mod_data['id']

  with open(token_file, 'r') as fin:
    payload['token'] = fin.readline().rstrip()

  print(f"payload = {json.dumps(payload, indent=2)}")
  pipeline_url = f"{gitlab_url}/api/v4/projects/{project_id}/trigger/pipeline"
  print(f"Triggering pipeline: {pipeline_url}")
  response = requests.post(pipeline_url,
                           data=payload)
  response.raise_for_status()

  return response.json()


def wait_for_pipeline(pl_info: dict[str, str]) -> Json:
  wait_stats = ['created', 
                'waiting_for_resource', 
                'preparing',
                'pending',
                'running']
  while True:
    pl_stat = get_pipeline_status(pl_info)
    if not pl_stat.get('status', '') in wait_stats:
      break
    time.sleep(5)

  return pl_stat


@mcp.tool()
def execute_pipeline(config_file: str,
                     inp_var_dicts: list[dict[str, dict[str, str]]] = None,
                     bail_on_fail: bool = True) -> str:
  """Executes a gitlab pipeline provided a configuration file. Can optionally
     execute with specific variable values if provided.

     Args:
       config_file (str): The path to the pipeline configuration file to use.
       inp_var_dicts (list[dict[str, dict[str, str]]]): An optional list of
         dictionaries containing key/value pairs with additional variable values
         to submit to the pipeline. Each dictionary will result in another
         pipeline execution.  These dictionaries should provide the name of the
         variables in the keys and the values should have the following structure:
           {
             'value': str
           }
       bail_on_fail (bool): Boolean value indicating whether to stop execution
                            of subsequent pipelines if a pipeline execution fails.

     Returns:
       A list of dictionaries containing information about the gitlab pipelines that have been triggered.
  """
  cfg_dir = os.path.dirname(config_file)

  with open(config_file, 'r') as fin:
    cfg_data = json.load(fin)

  if inp_var_dicts is None:
    inp_var_dicts = [None]

  client = get_client()

  # Models
  mod_info = get_model_info(client,
                            cfg_data['models'],
                            cfg_dir)

  t = threading.Thread(target=exec_pipeline,
                       args=(mod_info, inp_var_dicts, cfg_data, cfg_dir, bail_on_fail))
  t.start()

  return f"Pipelines will be executed sequentially. Information about each pipeline can be found in time-stamped folders in the results directory as each pipeline executes. Models used in this pipeline are as follows: {json.dumps(mod_info, indent=2)}"


@mcp.tool()
def get_pipeline_status(pl_info: dict[str, Any]) -> Json:
  """Gets information about a gitlab pipeline.

     Args:
       pl_info (dict[str, Any]): A dictionary containing metadata used to query the
                                 pipeline status. This data structure is returned from the
                                 `execute_pipeline` tool or can be read from a
                                 file. This dictionary should have the following
                                 structure:
            {
              'id': str,
              'gitlab_url': str,
              'project_id': str
            }

     Returns:
       A dictionary with information about the pipeline status.
  """
  gitlab_url = pl_info['gitlab_url']
  pipeline_id = pl_info['id']
  project_id = pl_info['project_id']
  pipeline_url = f"{gitlab_url}/api/v4/projects/{project_id}/pipelines/{pipeline_id}"
  header = {'PRIVATE-TOKEN': os.environ['GITLAB_TOKEN']}

  response = requests.get(pipeline_url, 
                          headers=header)
  return response.json()


@mcp.tool()
def get_workflow_info(workflow_dir: str) -> Json:
  """Gets information about an instance of a pipeline execution or workflow
     given the workflow results directory.

     Args:
       workflow_dir (str): The workflow results directory.

     Returns:
       A dictionary containing information about the workflow.
  """
  workflow_file = os.path.join(workflow_dir,
                               'workflow_info.json')
  if not os.path.exists(workflow_file):
    raise FileNotFoundError(f"Workflow information file not found: {workflow_file}")

  with open(workflow_file, 'r') as fin:
    pl_info = json.load(fin)

  return pl_info


if __name__ == "__main__":
  print("MCP Server is running")
  mcp.run(transport='stdio')
