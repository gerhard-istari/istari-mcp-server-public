# Execution Environment
## General Setup

Extract the zip archive to the following directory, depending on operating
system:

### Windows
`%USERPROFILE%/istari_mcp/`

### MacOS
`$HOME/Library/istari_mcp/`

### Linux
`/opt/local/istari_mcp/`

Use the `env_template` as a guide for creating a `.env` file with the
appropriate values.  This file should be placed in the directory containing the
MCP executable binaries.

## Enovia Server

Create a new `Batch Service Authentication` within the Enovia web client by
clicking the compass and navigating to:

`Platform Manager --> 3DPassport Control Center --> Integration --> Batch Services`

Use the `enovia_env_template` as a guide for creating an `enovia.env` file with
the service name and secret from the newly created batch service.  This file
should be placed in the directory containing the MCP executable binaries.

## MCP Configuration

Copy the text from the `mcp.json` file into the LLM client-specific
configuration file:

### Roo Code
Update the project or global `mcp_settings.json` or `mcp.json` file
respectively.

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
