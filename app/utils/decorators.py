"""
Utility decorators for the AI Tool Server.
"""
import os
import asyncio
from functools import wraps
from typing import Any, Callable
from fastapi import HTTPException
from loguru import logger

def with_timeout(func: Callable) -> Callable:
    """
    Decorator to add timeout to route handlers.
    
    Args:
        func: The async function to wrap with timeout
        
    Returns:
        Callable: The wrapped function
        
    Raises:
        HTTPException: If the operation times out
    """
    timeout = int(os.getenv("TIMEOUT", "10"))
    
    @wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return await asyncio.wait_for(func(*args, **kwargs), timeout=timeout)
        except asyncio.TimeoutError:
            logger.warning(f"Operation timed out after {timeout} seconds")
            return {
                "warning": f"Operation timed out after {timeout} seconds",
                "message": "The request was processed but took longer than expected. Please try again or contact support if this persists."
            }
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    return wrapper 
