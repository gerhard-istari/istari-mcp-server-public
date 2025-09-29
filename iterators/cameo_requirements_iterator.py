import json

from pydantic import Json


class CameoRequirementsIterator():
  def __init__(self,
               req_json: Json[dict]) -> None:
    self.req_json = req_json
    self.req_count = len(req_json)
    self.req_idx = 0


  def __iter__(self) -> object:
    return self


  def __next__(self) -> Json[dict]:
    if self.req_idx >= self.req_count:
      raise StopIteration

    ret_json = self.req_json[self.req_idx]
    self.req_idx += 1
    return ret_json

