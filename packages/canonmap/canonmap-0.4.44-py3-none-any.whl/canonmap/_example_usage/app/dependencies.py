from fastapi import Depends
from canonmap.connectors.mysql_connector.mysql_db_client import DBClient

def get_db_client() -> DBClient:
    """Get database client from app state."""
    # This will be used as a dependency in FastAPI routes
    pass

def get_db_client_dependency(request) -> DBClient:
    """Dependency function to get database client from request."""
    return DBClient(request.app.state.connector)
