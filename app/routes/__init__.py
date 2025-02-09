"""
Routes package for the AI Tool Server.
"""

from .sql_query_tool import router as sql_query_router

__all__ = ["sql_query_router"]
