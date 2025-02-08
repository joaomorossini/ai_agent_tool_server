from typing import List
from langchain_community.utilities import SQLDatabase
from langchain_community.tools.sql_database.tool import ListSQLDatabaseTool
from fastapi import APIRouter, HTTPException
import os
from dotenv import load_dotenv
from loguru import logger

router = APIRouter()

@router.get("/list_tables", response_model=List[str])
async def list_tables() -> List[str]:
    """
    Endpoint to list the available tables in a database.
    
    Returns:
        List[str]: A list of table names in the database
        
    Raises:
        HTTPException: If there's an error connecting to the database or fetching the tables
    """
    try:
        # Get database URI from environment
        database_uri = os.getenv("DATABASE_URI")
        if not database_uri:
            logger.error("DATABASE_URI environment variable not set")
            raise HTTPException(
                status_code=500,
                detail="Database configuration error"
            )

        # Connect to the database
        target_db = SQLDatabase.from_uri(database_uri)
        tool = ListSQLDatabaseTool(db=target_db)
        
        # Get tables and convert to list
        tables_str = tool._run()
        if not tables_str:
            return []
            
        # Split the comma-separated string and clean up whitespace
        tables = [table.strip() for table in tables_str.split(",")]
        return tables
        
    except Exception as e:
        logger.error(f"Error listing tables: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error listing tables: {str(e)}"
        )
