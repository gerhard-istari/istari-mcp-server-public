import dotenv
import os

dotenv.load_dotenv()

CAD_TOOL_NAME = 'dassault_3dexperience'
CAMEO_TOOL_NAME = 'dassault_cameo'
CAMEO_VERSION = os.getenv('CAMEO_VERSION')

REG_URL = os.getenv('REG_URL')
REG_AUTH_TOKEN = os.getenv('REG_AUTH_TOKEN')
CAD_MODEL_ID = os.getenv('CAD_MODEL_ID')
CAMEO_MODEL_ID = os.getenv('CAMEO_MODEL_ID')

REQ_FILE_NAME = 'requirements.json'
PARAM_FILE_NAME = 'parameters.json'
PARTS_FILE_NAME = 'parts.json'
UPDATE_PARAM_FILE_NAME = 'update_parameters.json'

GREEN_COLOR = 32
RED_COLOR = 31
BOLD_FORMAT = 1
