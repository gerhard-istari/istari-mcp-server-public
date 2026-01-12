import json
import logging
import os
import random

from io import BytesIO
from mcp.server.fastmcp import FastMCP
from PIL import Image
from pydantic import Json
from typing import Optional

from iterators.pdf_page_iterator import PdfPageIterator
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
    return extract_pdf_artifacts(**model_id)

  job = submit_job(model_id = model_id,
                   function = '@istari:extract',
                   tool_name = PDF_TOOL_NAME,
                   operating_system = 'Windows 11')
  print(f"Job submitted with ID: {job.id}")

  job = wait_for_job(job)
  return f"Job Complete [{job.status.name}]"


@mcp.tool()
async def get_pdf_pages(model_id: str,
                        query: Optional[list[str]] = None) -> str:
  """Retrieves pages from a pdf document with the specified model ID.
     If a query string is specified, iterates through all pages and returns
     those relevant to the submitted query.

     Args:
       model_id (str): The ID of the pdf document containing the pages.
       query (list[str]): A list of query strings. If any queries are a match,
       the page will be returned. If empty or omitted, returns all
       pages.
  """
  pgs_json = []
  try:
    pdf_data = download_artifact_data(model_id,
                                      PDF_TEXT_FILE_NAME)
    pdf_str = pdf_data.decode('utf-8')
    pdf_json = json.loads(pdf_str)
  except FileNotFoundError:
    return 'Artifact not found. Extract the artifacts from the pdf document first.'

  if query and len(query):
    pdf_iter = PdfPageIterator(pdf_json)
    print('Searching pages')
    matches = await search_artifact_data(query,
                                         pdf_iter)
    print('Search complete')
    print(f"Page Matches: {len(matches)}")
  else:
    matches = pdf_json

  return json.dumps(matches)


if __name__ == "__main__":
  print("MCP Server is running")
  mcp.run(transport='stdio')
