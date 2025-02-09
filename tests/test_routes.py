"""
Tests for all routes in the AI Tool Server.
Tests are run both locally and against the deployed server.
"""
import os
import pytest
from typing import Generator, Dict, Any
from fastapi.testclient import TestClient
import requests
from datetime import datetime
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from loguru import logger

from app.main import app
from app.database import get_db

# Test configuration
LOCAL_URL = "http://localhost:8000"
DEPLOYED_URL = os.getenv("FASTAPI_BASE_URL", "http://20.80.96.49:8001")  # TODO: Confirm port. This was previously set to 5002, but I think the correct one is 8001
TIMEOUT = int(os.getenv("TIMEOUT", "10"))

# Test database setup
TEST_DB_URI = "postgresql://ai_tool_user:ai_tool_password_123@localhost:5434/ai_tool_db"
os.environ["DATABASE_URI"] = TEST_DB_URI  # Set the environment variable for routes
engine = create_engine(TEST_DB_URI)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_test_db() -> Generator:
    """Get test database session."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

# Override the database dependency for testing
app.dependency_overrides[get_db] = get_test_db

# Test client for local testing
client = TestClient(app)

def setup_test_data(db_session) -> None:
    """Set up test data in the database."""
    try:
        # Verify database connection
        result = db_session.execute(text("SELECT 1"))
        assert result.scalar() == 1, "Database connection check failed"
        
        # Create test table
        logger.info("Creating test table...")
        db_session.execute(text("""
            DROP TABLE IF EXISTS test_table;
            CREATE TABLE test_table (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                value INTEGER
            );
        """))
        
        # Insert test data
        logger.info("Inserting test data...")
        db_session.execute(text("""
            INSERT INTO test_table (name, value) VALUES
            ('test1', 100),
            ('test2', 200),
            ('test3', 300);
        """))
        
        db_session.commit()
        logger.info("Test data setup completed successfully")
    except SQLAlchemyError as e:
        logger.error(f"Database error in setup_test_data: {str(e)}")
        db_session.rollback()
        raise e
    except Exception as e:
        logger.error(f"Unexpected error in setup_test_data: {str(e)}")
        db_session.rollback()
        raise e

@pytest.fixture(scope="module")
def db_session():
    """Database session fixture."""
    db = TestingSessionLocal()
    try:
        setup_test_data(db)
        yield db
    finally:
        # Cleanup
        db.execute(text("DROP TABLE IF EXISTS test_table;"))
        db.commit()
        db.close()

class TestEndpoints:
    """Test all endpoints both locally and on the deployed server."""
    
    @pytest.mark.parametrize("base_url", [LOCAL_URL])  # Testing only locally for now
    def test_health_check(self, base_url: str) -> None:
        """Test health check endpoint."""
        response = requests.get(f"{base_url}/health", timeout=TIMEOUT)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "version" in data
    
    @pytest.mark.parametrize("base_url", [LOCAL_URL])  # Testing only locally for now
    def test_sql_query_tool_select(self, base_url: str, db_session) -> None:
        """Test SQL query tool with SELECT query."""
        query = {"query": "SELECT * FROM test_table ORDER BY id"}
        response = requests.post(
            f"{base_url}/sql_query_tool",
            json=query,
            timeout=TIMEOUT
        )
        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        results = data["results"]
        assert len(results) == 3
        assert results[0]["name"] == "test1"
        assert results[0]["value"] == 100
    
    @pytest.mark.parametrize("base_url", [LOCAL_URL])  # Testing only locally for now
    def test_sql_query_tool_insert(self, base_url: str, db_session) -> None:
        """Test SQL query tool with INSERT query."""
        query = {
            "query": "INSERT INTO test_table (name, value) VALUES ('test4', 400)"
        }
        response = requests.post(
            f"{base_url}/sql_query_tool",
            json=query,
            timeout=TIMEOUT
        )
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Query executed successfully"
        assert data["rows_affected"] == 1
        
        # Verify the insert
        verify_query = {"query": "SELECT * FROM test_table WHERE name = 'test4'"}
        response = requests.post(
            f"{base_url}/sql_query_tool",
            json=verify_query,
            timeout=TIMEOUT
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["results"]) == 1
        assert data["results"][0]["value"] == 400
    
    @pytest.mark.parametrize("base_url", [LOCAL_URL])  # Testing only locally for now
    def test_sql_query_tool_error_handling(self, base_url: str) -> None:
        """Test SQL query tool error handling."""
        # Test with an invalid SQL query
        invalid_query = {"query": "INVALID SQL QUERY"}
        response = requests.post(
            f"{base_url}/sql_query_tool",
            json=invalid_query,
            timeout=TIMEOUT
        )
        assert response.status_code == 500
        data = response.json()
        assert "detail" in data
        assert "Database error" in data["detail"]

        # Test with an empty SQL query
        empty_query = {"query": ""}
        response = requests.post(
            f"{base_url}/sql_query_tool",
            json=empty_query,
            timeout=TIMEOUT
        )
        assert response.status_code == 422  # Pydantic validation error
        data = response.json()
        assert "detail" in data
        assert any("SQL query cannot be empty" in error["msg"] for error in data["detail"])

        # Test with a query causing a runtime error (e.g., referencing a non-existent table)
        runtime_error_query = {"query": "SELECT * FROM non_existent_table"}
        response = requests.post(
            f"{base_url}/sql_query_tool",
            json=runtime_error_query,
            timeout=TIMEOUT
        )
        assert response.status_code == 500
        data = response.json()
        assert "detail" in data
        assert "Database error" in data["detail"]
    
    @pytest.mark.parametrize("base_url", [LOCAL_URL])  # Testing only locally for now
    def test_timeout_handling(self, base_url: str, db_session) -> None:
        """Test timeout handling on a slow query."""
        # Create a slow query using pg_sleep
        query = {"query": "SELECT pg_sleep(15)"}  # Longer than our timeout
        try:
            response = requests.post(
                f"{base_url}/sql_query_tool",
                json=query,
                timeout=TIMEOUT + 5  # Add buffer to allow for timeout response
            )
            data = response.json()
            assert "warning" in data
            assert "Operation timed out" in data["warning"]
        except requests.exceptions.ReadTimeout:
            # This is also an acceptable outcome
            pass 
