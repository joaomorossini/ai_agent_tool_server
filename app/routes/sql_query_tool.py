"""
SQL Query Tool route for the AI Tool Server.
"""
from typing import Dict, Any, Optional

from fastapi import APIRouter, Depends, HTTPException
from loguru import logger
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from ..database import get_db

router = APIRouter()

@router.post("/sql_query_tool")
async def execute_sql_query(
    query: Dict[str, Any],
    db=Depends(get_db)
) -> Dict[str, Any]:
    """
    Execute a SQL query on the database.
    
    Args:
        query: A dictionary containing the SQL query to execute.
            Expected format: {"query": "SELECT * FROM table_name"}
        db: Database session dependency.
    
    Returns:
        Dict[str, Any]: A dictionary containing the query results.
            Format: {"results": [{"column": "value", ...}, ...]}
    
    Raises:
        HTTPException: If the query is invalid or fails to execute.
    """
    try:
        sql_query = query.get("query")
        if not sql_query:
            raise HTTPException(
                status_code=400,
                detail="No SQL query provided in request body"
            )
        
        # Execute the query
        result = db.execute(text(sql_query))
        
        # If the query is a SELECT, fetch results
        if sql_query.strip().upper().startswith("SELECT"):
            rows = result.fetchall()
            # Convert rows to list of dicts
            results = [dict(row._mapping) for row in rows]
            return {"results": results}
        
        # For non-SELECT queries, commit and return affected rows
        db.commit()
        return {"message": "Query executed successfully", "rows_affected": result.rowcount}
        
    except HTTPException as e:
        logger.error(f"Bad request: {str(e)}")
        raise e
    except SQLAlchemyError as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Database error: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error: {str(e)}"
        ) 
