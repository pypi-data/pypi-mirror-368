from typing import Any, List, Optional, TypedDict

from pydantic import BaseModel


class DmlResult(TypedDict):
    affected_rows: int

class QueryRequest(BaseModel):
    query: str
    params: Optional[List[Any]] = None

class QueryResult(BaseModel):
    rows: Optional[List[dict]] = None
    affected_rows: Optional[int] = None
