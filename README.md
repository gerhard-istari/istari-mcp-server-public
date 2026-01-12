# Execution Environment
## General Setup

Use the `env_template` as a guide for creating a `.env` file with the
appropriate values.

## Gitlab Server

### General Setup
The creation of a Personal Access Token (PAT) and the Istari Gitlab environment
file enables the server to query information about pipeline executions and other
general Gitlab information.

To create a Gitlab PAT:
    * Navigate to personal account preferences
    * Click on `Access tokens`
    * Click the `Add new token` button
    * Give the token a name and copy the token string
    * Edit the `gitlab.env` file in the Istari MCP installation directory and
      replace the value for the `GITLAB_TOKEN` with the copied token.

### Gitlab-Istari Workflow Configurations
Gitlab-Istari workflows can be configured with a json configuration file
containing information about the Gitlab pipeline, models and workflow inputs.  A
sample configuration file `sample_workflow.json` can be found in the
installation package.  Note that the `token_file` field should be the path to a
file that contains a trigger token for the associated pipeline.

To generate a project trigger token:
    * Navigate to the project page in Gitlab 
    * Click on `Settings`
    * Click on `CI/CD`
    * Expand the `Pipeline trigger tokens` section
    * Click the `Add new token` button
    * Copy the generated token and paste it to a file
    * Add this path to the `token_file` field in the workflow config file

Update the other Gitlab pipeline fields.  Specify a directory where pipeline
execution results can be stored.  Time stamped subdirectories will be created
for each pipeline execution.  Specify all models required for the pipeline and
any parameter inputs.

## Enovia Server
Create a new `Batch Service Authentication` within the Enovia web client by
clicking the compass and navigating to:

`Platform Manager --> 3DPassport Control Center --> Integration --> Batch Services`

Use the `enovia_env_template` as a guide for creating an `enovia.env` file with
the service name and secret from the newly created batch service.

## MCP Configuration
Copy the text from the `mcp.json` file into the LLM client-specific
configuration file.  The `command` entries for each of the MCP server commands
should be updated to the fully qualified paths to the extracted MCP server
binaries.

### Roo Code
Update the project or global mcp_settings.json file.

### Cline
Update the `cline_mcp_settings.json` file.

### Claude
Update the Claude desktop config file (claude_desktop_config.json).


# Build & Package
These steps are only required for building the MCP server package from source.

Set up a Python virtual environment:

### Windows
```bash
python -m venv venv
.\venv\Scripts\activate
```

### Linux/MacOS
```bash
python -m venv venv
source ./venv/bin/activate
```

Install dependencies:

```bash
pip install poetry
poetry install
```

Build the binaries:

```bash
poetry run poe build
```
This creates all of the MCP server binaries in the distribution `dist`
directory.


Package for deployment:
```bash
poetry run poe package
```
This generates a zip archive in the `dist` folder containing all MCP binaries
and associated resources that can be deployed to artifactory.
