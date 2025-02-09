from typing import List, Optional
from langchain_community.utilities import SQLDatabase
from langchain_community.tools.sql_database.tool import ListSQLDatabaseTool
from fastapi import APIRouter, HTTPException, Response
import os
from dotenv import load_dotenv
from loguru import logger
from functools import lru_cache
from datetime import datetime, timedelta

router = APIRouter()

# Cache the database connection
@lru_cache()
def get_database():
    """
    Get a cached database connection.
    
    Returns:
        SQLDatabase: A database connection instance
        
    Raises:
        ValueError: If the database configuration is invalid
    """
    database_uri = os.getenv("DATABASE_URI")
    if not database_uri:
        raise ValueError("DATABASE_URI environment variable not set")
    return SQLDatabase.from_uri(database_uri)

# Cache the list of tables for 5 minutes
@lru_cache()
def get_cached_tables(timestamp: str) -> List[str]:
    """
    Get a cached list of tables. The timestamp parameter is used to invalidate the cache every 5 minutes.
    
    Args:
        timestamp (str): Current timestamp rounded to 5-minute intervals
        
    Returns:
        List[str]: A list of table names
    """
    db = get_database()
    tool = ListSQLDatabaseTool(db=db)
    tables_str = tool._run()
    if not tables_str:
        return []
    return [table.strip() for table in tables_str.split(",")]

@router.get(
    "/list_tables",
    response_model=List[str],
    responses={
        200: {
            "description": "List of tables in the database",
            "content": {
                "application/json": {
                    "example": ["table1", "table2"]
                }
            }
        },
        500: {
            "description": "Database error",
            "content": {
                "application/json": {
                    "example": {"detail": "Error connecting to database"}
                }
            }
        }
    }
)
async def list_tables(response: Response) -> List[str]:
    """
    List all tables in the configured database.
    
    The results are cached for 5 minutes to improve performance and reduce database load.
    
    Returns:
        List[str]: A list of table names in the database
        
    Raises:
        HTTPException: If there's an error connecting to the database or fetching the tables
    """
    try:
        # Round current time to 5-minute intervals for cache key
        now = datetime.now()
        cache_key = now.replace(
            minute=5 * (now.minute // 5),
            second=0,
            microsecond=0
        ).isoformat()
        
        # Get tables from cache
        tables = get_cached_tables(cache_key)
        
        # Set cache control headers
        response.headers["Cache-Control"] = "public, max-age=300"
        
        return tables
        
    except ValueError as e:
        logger.error(f"Configuration error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Database configuration error"
        )
    except Exception as e:
        logger.error(f"Error listing tables: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error connecting to database"
        )
