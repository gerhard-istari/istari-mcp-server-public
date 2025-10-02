import json
import logging
import os
import random
import tempfile

from io import BytesIO
from mcp.server.fastmcp import FastMCP
from PIL import Image
from pydantic import Json
from typing import Optional

from shared.constants import *
from shared.helpers import *


mcp = FastMCP("istari-mcp-server")


@mcp.tool()
def extract_pdf_artifacts(model_id: str) -> str:
  """Extracts artifacts from a PDF document with the specified ID.

     Args:
       model_id (str): A string containing the ID of the model to extract artifacts.
  """
  if isinstance(model_id, dict):
    return extract_pdf_model_artifacts(**model_id)

  job = submit_job(model_id = model_id,
                   function = '@istari:extract',
                   tool_name = PDF_TOOL_NAME)
  print(f"Job submitted with ID: {job.id}")

  job = wait_for_job(job)
  return f"Job Complete [{job.status.name}]"


if __name__ == "__main__":
  print("MCP Server is running")
  mcp.run(transport='stdio')
