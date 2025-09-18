# Build
```bash
python -m venv venv
pip install poetry
poetry install
poetry run poe build
```

This creates all of the MCP server binaries in the distribution `dist`
directory.

# Environment
## General Setup

Use the `env_template` as a guide for creating a `.env` file with the
appropriate values.

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

### Claude
Update the Claude desktop config file (claude_desktop_config.json).
