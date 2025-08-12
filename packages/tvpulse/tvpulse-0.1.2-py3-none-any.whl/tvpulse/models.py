from typing import List, Optional
from pydantic import BaseModel


class DataPoint(BaseModel):
  """
  Represents a single data point in the API response.
  """
  stream: str
  date_time: str
  count: int
  source: Optional[str] = None


class APIResponse(BaseModel):
  """
  Represents the overall API response.
  """
  data: List[DataPoint]
  next_page_token: Optional[str] = None
