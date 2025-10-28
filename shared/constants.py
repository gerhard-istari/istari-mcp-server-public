import dotenv
import os
import sys


def is_executable() -> bool:
  exe_file = os.path.basename(sys.executable)
  exe_name = os.path.splitext(exe_file)[0]
  return exe_name.lower() != 'python'


if is_executable():
  dotenv_file = os.path.join(os.path.dirname(sys.executable),
                             '.env')
  dotenv.load_dotenv(dotenv_path=dotenv_file)
else:
  dotenv.load_dotenv()

CAD_TOOL_NAME = 'dassault_3dexperience'
CAMEO_TOOL_NAME = 'dassault_cameo'
CAMEO_VERSION = os.getenv('CAMEO_VERSION')
EXCEL_TOOL_NAME = 'microsoft_office_excel'
NASTRAN_TOOL_NAME = 'msc_nastran'
NASTRAN_EXTRACT_TOOL_NAME = 'nastran_extract'
PDF_TOOL_NAME = 'open_pdf'
PDF_TOOL_VERSION = '1.0.0'
SIMULINK_TOOL_NAME = 'matlab'

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
PDF_TEXT_FILE_NAME = 'text_sections.json'

GREEN_COLOR = 32
RED_COLOR = 31
BOLD_FORMAT = 1
