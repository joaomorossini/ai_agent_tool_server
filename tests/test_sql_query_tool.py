"""
Tests for the SQL query tool endpoint.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import get_db

# Use an in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

def setup_module():
    """Create test table and insert sample data."""
    db = TestingSessionLocal()
    # Drop the table if it exists
    db.execute(text("DROP TABLE IF EXISTS test_table"))
    db.commit()
    
    # Create the table
    db.execute(text("""
        CREATE TABLE IF NOT EXISTS test_table (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL
        )
    """))
    
    # Insert sample data
    db.execute(text("INSERT INTO test_table (id, name) VALUES (1, 'test1')"))
    db.execute(text("INSERT INTO test_table (id, name) VALUES (2, 'test2')"))
    db.commit()

def test_sql_query_tool_select():
    """Test SELECT query."""
    response = client.post(
        "/sql_query_tool",
        json={"query": "SELECT * FROM test_table"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert len(data["results"]) == 2
    assert data["results"][0]["name"] == "test1"

def test_sql_query_tool_insert():
    """Test INSERT query."""
    response = client.post(
        "/sql_query_tool",
        json={"query": "INSERT INTO test_table (id, name) VALUES (3, 'test3')"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Query executed successfully"
    assert data["rows_affected"] == 1

def test_sql_query_tool_invalid_query():
    """Test invalid SQL query."""
    response = client.post(
        "/sql_query_tool",
        json={"query": "INVALID SQL"}
    )
    assert response.status_code == 500
    assert "Database error" in response.json()["detail"]

def test_sql_query_tool_missing_query():
    """Test missing query parameter."""
    response = client.post(
        "/sql_query_tool",
        json={}
    )
    assert response.status_code == 400
    assert "No SQL query provided" in response.json()["detail"] 
