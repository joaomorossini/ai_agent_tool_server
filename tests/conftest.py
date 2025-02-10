"""
Pytest configuration file for the AI Tool Server tests.
"""
import os
import sys
import asyncio
from typing import AsyncGenerator
import pytest
import pytest_asyncio
import asyncpg
from asyncpg.pool import Pool
from fastapi.testclient import TestClient

from app.main import app
from app.database import DATABASE_URI

# Add the app directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Test database configuration
TEST_DATABASE_URI = os.getenv("TEST_DATABASE_URI", DATABASE_URI)

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest_asyncio.fixture(scope="session")
async def db_pool() -> AsyncGenerator[Pool, None]:
    """Create a database connection pool for tests."""
    pool = await asyncpg.create_pool(
        TEST_DATABASE_URI,
        min_size=2,
        max_size=10,
        command_timeout=30
    )
    
    # Create test tables
    async with pool.acquire() as conn:
        await conn.execute("""
            DROP TABLE IF EXISTS job_executions;
            DROP TABLE IF EXISTS jobs;
            DROP TYPE IF EXISTS execution_status;
            DROP TYPE IF EXISTS job_status;
            DROP TYPE IF EXISTS job_type;
            
            DO $$ BEGIN
                CREATE TYPE job_type AS ENUM ('one-time', 'interval', 'cron');
                CREATE TYPE job_status AS ENUM ('pending', 'active', 'completed', 'failed', 'cancelled');
                CREATE TYPE execution_status AS ENUM ('running', 'completed', 'failed');
            EXCEPTION
                WHEN duplicate_object THEN null;
            END $$;
            
            CREATE TABLE jobs (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                name VARCHAR(255) NOT NULL,
                type job_type NOT NULL,
                status job_status NOT NULL DEFAULT 'pending',
                schedule JSONB NOT NULL,
                parameters JSONB NOT NULL,
                next_run_time TIMESTAMP WITH TIME ZONE,
                last_run_at TIMESTAMP WITH TIME ZONE,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE TABLE job_executions (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                job_id UUID NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
                status execution_status NOT NULL DEFAULT 'running',
                started_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP WITH TIME ZONE,
                error TEXT,
                result JSONB,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            );
        """)
    
    yield pool
    
    # Cleanup
    async with pool.acquire() as conn:
        await conn.execute("""
            DROP TABLE IF EXISTS job_executions;
            DROP TABLE IF EXISTS jobs;
            DROP TYPE IF EXISTS execution_status;
            DROP TYPE IF EXISTS job_status;
            DROP TYPE IF EXISTS job_type;
        """)
    await pool.close()

@pytest_asyncio.fixture
async def db_conn(db_pool: Pool) -> AsyncGenerator[asyncpg.Connection, None]:
    """Get a database connection for tests."""
    async with db_pool.acquire() as conn:
        await conn.execute("BEGIN")
        # Recreate tables for each test
        await conn.execute("""
            DO $$ BEGIN
                CREATE TYPE IF NOT EXISTS job_type AS ENUM ('one-time', 'interval', 'cron');
                CREATE TYPE IF NOT EXISTS job_status AS ENUM ('pending', 'active', 'completed', 'failed', 'cancelled');
                CREATE TYPE IF NOT EXISTS execution_status AS ENUM ('running', 'completed', 'failed');
            EXCEPTION
                WHEN duplicate_object THEN null;
            END $$;
            
            DROP TABLE IF EXISTS job_executions;
            DROP TABLE IF EXISTS jobs;
            
            CREATE TABLE IF NOT EXISTS jobs (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                name VARCHAR(255) NOT NULL,
                type job_type NOT NULL,
                status job_status NOT NULL DEFAULT 'pending',
                schedule JSONB NOT NULL,
                parameters JSONB NOT NULL,
                next_run_time TIMESTAMP WITH TIME ZONE,
                last_run_at TIMESTAMP WITH TIME ZONE,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE TABLE IF NOT EXISTS job_executions (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                job_id UUID NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
                status execution_status NOT NULL DEFAULT 'running',
                started_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP WITH TIME ZONE,
                error TEXT,
                result JSONB,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            );
        """)
        try:
            yield conn
        finally:
            await conn.execute("ROLLBACK")

@pytest.fixture
def client() -> TestClient:
    """Get a test client."""
    return TestClient(app) 
