import json
import os
import platform

from zipfile import ZipFile


plat_sys = platform.system()
dist_dir = './dist'
mcp_json_file = f"mcp-{plat_sys}.json"
vers_file = 'VERSION'
res_files = [
  'README.md',
  'env_template',
  'enovia_env_template',
  'gitlab_env_template',
  'sample_workflow.json',
  mcp_json_file,
  vers_file,
]          

with open(vers_file, 'r') as fin:
  version = fin.readline().strip()

with open(mcp_json_file, 'r') as fin:
  mcp_json = json.load(fin)

zip_file = os.path.join(dist_dir,
                        f"istari-mcp-server-{plat_sys}-{version}.zip")
if os.path.exists(zip_file):
  os.remove(zip_file)

with ZipFile(zip_file, 'w') as fout:
  # Zip resource files
  for res_file in res_files:
    print(f"Packaging resource file: {res_file}")
    fout.write(res_file)

  # Package mcp servers
  for mcp_server in mcp_json['mcpServers'].values():
    mcp_server_name = os.path.basename(mcp_server['args'][1])
    bin_file = os.path.join(dist_dir,
                            mcp_server_name)
    if os.path.exists(bin_file):
      print(f"Packaging binaries: {mcp_server_name}")
      fout.write(bin_file,
                 arcname=mcp_server_name)
    else:
      print(f"Binary not found. Skipping: {mcp_server_name}")
