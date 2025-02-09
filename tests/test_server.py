import pytest
from httpx import AsyncClient, ASGITransport
from fastapi import FastAPI
from app.main import app
from datetime import datetime
from typing import AsyncGenerator
import pytest_asyncio

@pytest_asyncio.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """
    Fixture that creates an async client for testing.
    
    Yields:
        AsyncClient: An async client configured for testing the FastAPI application
    """
    async with AsyncClient(
        transport=ASGITransport(app=app), 
        base_url="http://test"
    ) as client:
        yield client

@pytest.mark.asyncio
async def test_health_check(async_client: AsyncClient) -> None:
    """
    Test the health check endpoint.
    
    Args:
        async_client: The async client fixture for making requests
        
    Asserts:
        - Response status code is 200
        - Response contains 'status' field with value 'healthy'
        - Response contains 'timestamp' field with valid ISO format
    """
    response = await async_client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] == "healthy"
    assert "timestamp" in data
    # Verify timestamp is in valid ISO format
    datetime.fromisoformat(data["timestamp"])

@pytest.mark.asyncio
async def test_root_endpoint(async_client: AsyncClient) -> None:
    """
    Test the root endpoint.
    
    Args:
        async_client: The async client fixture for making requests
        
    Asserts:
        - Response status code is 200
        - Response contains 'message' field with welcome message
    """
    response = await async_client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert data["message"] == "Welcome to the AI Tool Server"

@pytest.mark.asyncio
async def test_openapi_endpoint(async_client: AsyncClient) -> None:
    """
    Test the OpenAPI documentation endpoint.
    
    Args:
        async_client: The async client fixture for making requests
        
    Asserts:
        - Response status code is 200
        - OpenAPI version is at least 3.1.0
        - Contains basic OpenAPI information
    """
    response = await async_client.get("/openapi.json")
    assert response.status_code == 200
    data = response.json()
    assert data["openapi"] >= "3.1.0"  # Ensure at least version 3.1.0
    assert "info" in data
    assert data["info"]["title"] == "AI Tool Server"
    assert data["info"]["version"] == "1.0.0"
