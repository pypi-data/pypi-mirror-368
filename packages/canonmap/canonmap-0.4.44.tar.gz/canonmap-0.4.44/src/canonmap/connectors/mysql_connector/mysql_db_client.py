from typing import Any, List, Optional

from canonmap.connectors.mysql_connector.models import DmlResult
from canonmap.connectors.mysql_connector.mysql_connector import \
    MySQLConnector


class DBClient:
    """High-level DB client using MySQLConnector."""
    def __init__(self, connector: MySQLConnector):
        self._connector = connector

    def execute_read(self, query: str, params: Optional[List[Any]] = None) -> List[dict]:
        return self._connector.execute_query(query, params, allow_writes=False)  # type: ignore

    def execute_write(self, query: str, params: Optional[List[Any]] = None) -> DmlResult:
        return self._connector.execute_query(query, params, allow_writes=True)  # type: ignore