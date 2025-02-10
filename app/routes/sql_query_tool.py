"""
SQL Query Tool route for the AI Tool Server.
"""
from typing import Dict, Any
from fastapi import APIRouter, HTTPException
from loguru import logger
from pydantic import BaseModel, field_validator

from ..database import get_db_connection
from ..utils.decorators import with_timeout

router = APIRouter()

class SQLQuery(BaseModel):
    """Model for SQL query requests."""
    query: str
    
    @field_validator('query')
    @classmethod
    def validate_query(cls, v: str) -> str:
        """Validate that the query is not empty."""
        if not v:
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        return v

@router.post("/sql_query_tool")
@with_timeout
async def execute_sql_query(query_data: SQLQuery) -> Dict[str, Any]:
    """
    Execute a SQL query on the database.
    
    Args:
        query_data: A SQLQuery object containing the SQL query to execute.
    
    Returns:
        Dict[str, Any]: Query results or execution status.
    
    Raises:
        HTTPException: For invalid queries or execution errors.
    """
    try:
        sql_query = query_data.query  # Already validated by Pydantic
        logger.info(f"Executing SQL query: {sql_query}")
        
        async with get_db_connection() as conn:
            if sql_query.upper().strip().startswith("SELECT"):
                # For SELECT queries, return the results
                rows = await conn.fetch(sql_query)
                results = [dict(row) for row in rows]
                logger.info(f"Query returned {len(results)} rows")
                return {"results": results}
            else:
                # For non-SELECT queries, execute and return affected rows
                result = await conn.execute(sql_query)
                affected = int(result.split()[-1]) if result else 0
                logger.info(f"Query affected {affected} rows")
                return {
                    "message": "Query executed successfully",
                    "rows_affected": affected
                }
            
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Database error: {str(e)}"
        ) 
