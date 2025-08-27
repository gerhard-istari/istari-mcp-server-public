"""
This MCP server expects a file named 'enovia.env' to be located in the same
directory as the server. The env file must include the following information:

BASE_URL = <YOUR_BASE_URL>
SERVICE_NAME = <YOUR_SERVICE_NAME>
SERVICE_SECRET = <YOUR_SERVICE_SECRET>

A service secret can be generated from 3DX Platform Manager ->
3D Passport Control Center -> Integration -> Batch Services
"""
import json
import os
import requests
import urllib.parse
from mcp.server.fastmcp import FastMCP

from istari_digital_client.models.tracked_file_specifier_type import TrackedFileSpecifierType

from shared.constants import *
from shared.helpers import *


mcp = FastMCP("istari-mcp-server")
ec = None

class EnoviaConnector:

  def __init__(self):
    dotenv.load_dotenv(dotenv_path='enovia.env',override=True)
    self.BASE_URL = self._get_env_var('BASE_URL')


  def get_standard_header(self) -> dict[str, str]:
    return {"Accept": "application/json"}


  def get_session_header(self) -> dict[str, str]:
    header = self.get_standard_header()
    header['SecurityContext'] = self.security_context
    return header


  def get_3dspace_url(self) -> str:
    return f"{self.BASE_URL}/3dspace"


  def get_3dpassport_url(self) -> str:
    return f"{self.BASE_URL}/3dpassport"


  def get_engineering_url(self) -> str:
    return f"{self.get_3dspace_url()}/resources/v1/modeler/dseng"


  def get_documents_url(self) -> str:
    return f"{self.get_3dspace_url()}/resources/v1/modeler/documents"


  def get_issues_url(self) -> str:
    return f"{self.get_3dspace_url()}/resources/v1/modeler/dsiss/issue"


  def start_session(self):
    # Get TGT (Ticket Granting Ticket)
    SERVICE_NAME = self._get_env_var("SERVICE_NAME")
    SERVICE_SECRET = self._get_env_var("SERVICE_SECRET")
    headers = {
        "DS-SERVICE-NAME": SERVICE_NAME,
        "DS-SERVICE-SECRET": SERVICE_SECRET,
    }

    USERNAME = self._get_env_var("ENOVIA_USER")
    self.SSL_VERIFY = os.getenv("SSL_VERIFY")
    if self.SSL_VERIFY is None: self.SSL_VERIFY = True
    else: self.SSL_VERIFY = self.SSL_VERIFY.lower() != 'false'

    url = f"{self.get_3dpassport_url()}/api/v2/batch/ticket?identifier={USERNAME}&service={urllib.parse.quote(self.BASE_URL + '/3dspace/')}"
    response = requests.get(url, 
                            headers=headers,
                            verify=self.SSL_VERIFY)
    tgt = response.json()["access_token"]
    print(f"TGT Access Token: {tgt}")


    # Get ST (Service Ticket) from TGT
    url = f"{self.get_3dpassport_url()}/api/login/cas/transient?tgt={tgt}&service={urllib.parse.quote(self.BASE_URL + '/3dspace/')}"
    header = self.get_standard_header()
    response = requests.get(url, 
                            headers=header,
                            verify=self.SSL_VERIFY)
    st = response.json()["access_token"]
    print(f"ST Access Token: {st}")

    # Use ST to Authenticate Session
    self.session = requests.Session()
    auth_response = self.session.get(f"{self.get_3dspace_url()}/?ticket={st}",
                                     verify=self.SSL_VERIFY)

    # Save Security Context
    url = f"{self.get_3dspace_url()}/resources/modeler/pno/person"
    params = {
        "current": "true",
        "select": "preferredcredentials"
    }
    response = self.session.get(url, 
                                params=params, 
                                headers=header,
                                verify=self.SSL_VERIFY)
    response.raise_for_status()
    credentials = response.json()["preferredcredentials"]
    role = credentials["role"]["name"]
    organization = credentials["organization"]["name"]
    collabspace = credentials["collabspace"]["name"]
    self.security_context = f"{role}.{organization}.{collabspace}"


  def get_engineering_item(self,
                           item_id: str) -> None:
    url = f"{self.get_engineering_url()}/dseng:EngItem/{item_id}"
    resp = self.session.get(url,
                            headers=self.get_session_header(),
                            verify=self.SSL_VERIFY)
    print(json.dumps(resp.json(), indent=2))


  def find_engineering_items(self,
                             srch_str: str,
                             max_items: int = 1) -> object:
    url = f"{self.get_engineering_url()}/dseng:EngItem/search"
    params = {"$searchStr": srch_str, "$top": max_items}
    resp = self.session.get(url,
                            headers=self.get_session_header(),
                            params=params,
                            verify=self.SSL_VERIFY)
    return resp.json()


  def get_engineering_item_instances(self,
                                     item_id: str) -> object:
    url = f"{self.get_engineering_url()}/dseng:EngItem/{item_id}/dseng:EngInstance"
    resp = self.session.get(url,
                            headers=self.get_session_header(),
                            verify=self.SSL_VERIFY)
    return json.dumps(resp.json(), indent=2)


  def replace_engineering_instance(self,
                                   parent_id: str,
                                   component_id: str) -> str:
    url = f"{self.get_engineering_url()}/dseng:EngItem/{parent_id}/dseng:EngInstance/{component_id}/replace"
    print(url)
    resp = self.session.post(url,
                             headers=self.get_session_header(),
                             verify=self.SSL_VERIFY)
    print(json.dumps(resp.json(), indent=2))


  def get_item_documents(self,
                         item_id: str,
                         rels: list[str] = ["Reference Document", "PLMDocConnection", "SpecificationDocument"]) -> list[dict[str, str]]:
    docs = []
    for rel in rels:
      params = {
                 "parentRelName": rel,
                 "parentDirection": "from",
                 "$include": "files,ownerInfo,parents",
								 "$fields": "all"
                }
      url = f"{self.get_documents_url()}/parentId/{item_id}"
      resp = self.session.get(url,
                              params=params,
                              headers=self.get_session_header(),
                              verify=self.SSL_VERIFY)
      docs.append(resp.json())

    return docs


  def find_documents(self,
                     srch_str: str,
                     max_items: int = 1) -> object:
    url = f"{self.get_documents_url()}/search"
    params = {"searchStr": srch_str, "$top": max_items}
    resp = self.session.get(url,
                            headers=self.get_session_header(),
                            params=params,
                            verify=self.SSL_VERIFY)
    return resp.json()


  def find_issues(self,
                  srch_str: str,
                  max_items: int = 1) -> object:
    url = f"{self.get_issues_url()}/search"
    params = {"$searchStr": srch_str, "$top": max_items}
    resp = self.session.get(url,
                            headers=self.get_session_header(),
                            params=params,
                            verify=self.SSL_VERIFY)
    return resp.json()


  def get_issue(self,
                issue_id: str) -> object:
    url = f"{self.get_issues_url()}/{issue_id}"
    params = {"$fields": "all"}
    resp = self.session.get(url,
                            headers=self.get_session_header(),
                            params=params,
                            verify=self.SSL_VERIFY)
    return resp.json()


  def get_document_files(self,
                         doc_id: str) -> object:
    files_url = f"{self.get_documents_url()}/{doc_id}/files"
    resp = self.session.get(files_url,
                            headers=self.get_session_header(),
                            verify=self.SSL_VERIFY)
    resp.raise_for_status()
    file_json = resp.json()
    return file_json['data']


  def download_document_file(self,
                             doc_id: str,
                             file_id: str,
                             dest_file: str) -> None:
    base_url = f"{self.get_documents_url()}/{doc_id}"
    resp = self.session.get(base_url,
                            headers=self.get_session_header(),
                            verify=self.SSL_VERIFY)
    csrf_tok = resp.json().get('csrf', {}).get('value', '')

    ticket_url = f"{base_url}/files/{file_id}/DownloadTicket"
    header = self.get_session_header()
    header['ENO_CSRF_TOKEN'] = csrf_tok
    resp = self.session.put(ticket_url,
                            headers=header,
                            verify=self.SSL_VERIFY)
    resp.raise_for_status()
    download_json = resp.json()
    download_url = download_json['data'][0]['dataelements']['ticketURL']
    resp = self.session.get(download_url,
                            headers=self.get_session_header(),
                            verify=self.SSL_VERIFY,
                            allow_redirects=True)
    resp.raise_for_status()
    with open(dest_file, 'wb') as fout:
      fout.write(resp.content)


  def _get_env_var(self,
                   var_name: str) -> str:
    var_val = os.getenv(var_name)
    if var_val is None:
      raise EnvironmentError(f"[{var_name}] variable has not been set in environment")

    return var_val


@mcp.tool()
def get_engineering_item(item_id: str) -> dict[str, str]:
  """Gets an Enovia engineering item with the specified ID.

		 Args:
			 item_id (str): The engineering item ID

		 Returns:
       A dictionary with information about the engineering item such as name, ID, descriptions, etc.
  """
  return ec.get_engineering_item(item_id)


@mcp.tool()
def find_engineering_items(srch_str: str) -> list[dict[str, str]]:
  """Finds all Enovia engineering items that match the specified search string.

		 Args:
			 srch_str (str): The string to use for matching product names

		 Returns:
       A list of engineering item dictionaries with information about the items such as name, ID, description, etc.
  """
  return ec.find_engineering_items(srch_str, 
                                   100)

@mcp.tool()
def get_engineering_item_instances(item_id: str) -> list[dict[str, str]]:
  """Gets all instances (subassemblies, subcomponents, parts, etc.) of the specified engineering item.

     Args:
       item_id (str): The engineering item ID to search

     Returns:
       A list of engineering instance dictionaries with information about the instances such as name, ID, description, etc.
  """
  return ec.get_engineering_item_instances(item_id)


@mcp.tool()
def get_item_documents(item_id: str,
                       relationships: list[str] = ["Reference Document", "PLMDocConnection", "SpecificationDocument"]) -> list[dict[str, str]]:
  """Gets documents associated with an engineering item.

     Args:
       item_id (str): The engineering item ID
       relationships (list[str]): The types of relationships of the associated documents to search for

     Return:
       A list of document dictionaries with information about the documents such as name, ID, description, etc.
  """
  return ec.get_item_documents(item_id,
                               relationships)


@mcp.tool()
def find_documents(srch_str: str) -> list[dict[str, str]]:
  """Finds all Enovia documents that match the specified search string.

		 Args:
			 srch_str (str): The string to use for matching documents

		 Returns:
       A list of document dictionaries with information about the documents such as name, ID, description, etc.
  """
  return ec.find_documents(srch_str, 
                           100)


@mcp.tool()
def find_issues(srch_str: str) -> list[dict[str, str]]:
  """Finds all Enovia issues that match the specified search string.

		 Args:
			 srch_str (str): The string to use for matching issues

		 Returns:
       A list of issue dictionaries with information about the issues such as name, ID, description, etc.
  """
  return ec.find_issues(srch_str, 
                        100)


@mcp.tool()
def get_issue(issue_id: str) -> dict[str, str]:
  """Gets an Enovia issue with the specified ID.

		 Args:
			 issue_id (str): The issue ID

		 Returns:
       A dictionary containing information about the issue such as name, ID, description, etc.
  """
  return ec.get_issue(issue_id)


@mcp.tool()
def get_document_files(doc_id: str) -> list[dict[str, str]]:
  """Gets the files associated with a document with the specified ID.

     Args:
       doc_id (str): The document ID

     Returns:
       A list of dictionaries containing information about the associated files such as name, ID, description, etc.
  """
  return ec.get_document_files(doc_id)


@mcp.tool()
def download_document_file(doc_id: str,
                           file_id: str,
                           dest_file: str) -> str:
  """Downloads the specified file referenced (attached) by the specified document.

     Args:
       doc_id (str): The document ID
       file_id (str): The file ID
       dest_file (str): The path to the location to save the file
  """
  ec.download_document_file(doc_id,
                            file_id,
                            dest_file)
  print(f"Document file downloaded successfully")


if __name__ == "__main__":
  ec = EnoviaConnector()
  ec.start_session()
  print("MCP Server is running")
  mcp.run(transport='stdio')
