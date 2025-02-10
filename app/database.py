"""
Database module for the AI Tool Server.
Provides async database connection handling using asyncpg.
"""
import os
from typing import AsyncGenerator
from contextlib import asynccontextmanager
import asyncpg
from asyncpg.pool import Pool

# Get database URI from environment variable
DATABASE_URI = os.getenv("DATABASE_URI")
if not DATABASE_URI:
    raise ValueError("DATABASE_URI environment variable is not set")

# Global connection pool
_pool: Pool = None

async def get_pool() -> Pool:
    """
    Get or create the database connection pool.
    
    Returns:
        Pool: The asyncpg connection pool
    """
    global _pool
    if _pool is None:
        _pool = await asyncpg.create_pool(
            DATABASE_URI,
            min_size=5,
            max_size=20,
            command_timeout=60
        )
    return _pool

@asynccontextmanager
async def get_db_connection() -> AsyncGenerator[asyncpg.Connection, None]:
    """
    Get a database connection from the pool.
    
    Yields:
        Connection: An asyncpg connection object.
        
    Example:
        async with get_db_connection() as conn:
            result = await conn.fetch("SELECT * FROM my_table")
    """
    pool = await get_pool()
    async with pool.acquire() as conn:
        yield conn

async def close_pool() -> None:
    """
    Close the database connection pool.
    Should be called when shutting down the application.
    """
    global _pool
    if _pool:
        await _pool.close()
        _pool = None 
