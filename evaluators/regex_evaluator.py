import re

from evaluators.query_status import QueryStatus


async def evaluate_query(queries: list[str],
                         item: str) -> QueryStatus:
  if not isinstance(item, str):
    item = str(item)

  ret_val = QueryStatus.MISS
  for query in queries:
    if re.search(query, item, re.IGNORECASE):
      ret_val = QueryStatus.MATCH
      break

  return ret_val
