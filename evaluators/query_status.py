from enum import Enum

class QueryStatus(Enum):
  MATCH = 1
  MISS  = 2
  FAIL  = 3
