# Environment
## System

Set up the Python environment:

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

Use the env_template as a guide for creating a .env file with the appropriate values.

## Roo Code
Copy the text from the OS-appropriate mcp.json file into the Roo Code global mcp_settings.json file.

