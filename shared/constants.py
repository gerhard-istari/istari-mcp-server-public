import dotenv
import os

dotenv.load_dotenv()

CAD_TOOL_NAME = 'dassault_3dexperience'
CAMEO_TOOL_NAME = 'dassault_cameo'
CAMEO_VERSION = os.getenv('CAMEO_VERSION')
EXCEL_TOOL_NAME = 'microsoft_office_excel'
NASTRAN_TOOL_NAME = 'msc_nastran'
NASTRAN_EXTRACT_TOOL_NAME = 'nastran_extract'

REG_URL = os.getenv('REG_URL')
REG_AUTH_TOKEN = os.getenv('REG_AUTH_TOKEN')
CAD_MODEL_ID = os.getenv('CAD_MODEL_ID')
CAMEO_MODEL_ID = os.getenv('CAMEO_MODEL_ID')

REQ_FILE_NAME = 'requirements.json'
PARAM_FILE_NAME = 'parameters.json'
PARTS_FILE_NAME = 'parts.json'
UPDATE_PARAM_FILE_NAME = 'update_parameters.json'
NAMED_CELLS_FILE_NAME = 'named_cells.json'
MOD_WB_FILE_NAME = 'modified_workbook.xlsx'
OP2_SUMMARY_FILE_NAME = 'op2_summary.json'
NASTRAN_RESULTS_FILE_NAME = 'model.op2'
MAT_SUMMARY_FILE_NAME = 'material_summary.json'

GREEN_COLOR = 32
RED_COLOR = 31
BOLD_FORMAT = 1
