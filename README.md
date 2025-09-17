# Environment
## General

Use the `env_template` as a guide for creating a `.env` file with the appropriate values.

## Enovia Server

Create a new `Batch Service Authentication` within the Enovia web client by clicking the compass and navigating to:

`Platform Manager --> 3DPassport Control Center --> Integration --> Batch Services

Use the `enovia_env_template` as a guide for creating an `enovia.env` file with the service name and secret from the
newly created batch service.

## System

Set up the Python environment within the MCP repo:

### Windows
```bash
python -m venv venv
.\venv\Scripts\activate
pip install poetry
poetry install
```

### Linux/MacOS
```bash
python -m venv venv
source venv/bin/activate
pip install poetry
poetry install
```

## Roo Code
Copy the text from the OS-appropriate mcp.json file into the Roo Code global mcp_settings.json file.

## Claude
Copy the text from the OS-appropriate mcp.json file into the Claude desktop config file (claude_desktop_config.json).
