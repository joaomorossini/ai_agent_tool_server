"""
Routes package for the AI Tool Server.
"""

from .list_tables_tool import router as list_tables_router
from .sql_query_tool import router as sql_query_router

__all__ = ["list_tables_router", "sql_query_router"]
