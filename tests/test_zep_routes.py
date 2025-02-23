import pytest
from unittest.mock import AsyncMock, patch
from fastapi import FastAPI
from fastapi.testclient import TestClient
from app.routes.tools.zep_routes import router
from app.services.zep_service import ZepService
from app.models.zep_models import (
    UserBase, UserResponse, SessionCreate, SessionResponse,
    MemoryAdd, MemoryResponse, GraphData, GraphSearchParams,
    GraphSearchResponse, Fact
)

app = FastAPI()
app.include_router(router)
client = TestClient(app)

# Mock data
MOCK_USER_DATA = {
    "first_name": "John",
    "last_name": "Doe",
    "email": "john@example.com",
    "metadata": {"key": "value"}
}

MOCK_SESSION_DATA = {
    "user_id": "john_doe_123",
    "metadata": {"session_key": "value"}
}

MOCK_MEMORY_DATA = {
    "session_id": "session_123",
    "chat_history": [
        {"role": "user", "content": "Hello", "name": "John"},
        {"role": "assistant", "content": "Hi there!", "name": None}
    ],
    "return_context": True
}

MOCK_GRAPH_DATA = {
    "data": {"key": "value"},
    "group_id": "group_123",
    "data_type": "test",
    "user_id": "user_123"
}

MOCK_GRAPH_SEARCH_PARAMS = {
    "query": "test query",
    "limit": 5,
    "reranker": "rrf",
    "scope": "edges"
}


@pytest.fixture
def mock_zep_service():
    with patch("app.routes.tools.zep_routes.ZepService") as mock:
        service_instance = AsyncMock(spec=ZepService)
        mock.return_value = service_instance
        yield service_instance


@pytest.mark.asyncio
async def test_create_user(mock_zep_service):
    """Test user creation endpoint"""
    mock_response = UserResponse(
        user_id="john_doe_123",
        **MOCK_USER_DATA
    )
    mock_zep_service.add_user.return_value = mock_response

    response = client.post("/tools/zep/users", json=MOCK_USER_DATA)
    assert response.status_code == 200
    assert response.json()["user_id"] == "john_doe_123"
    assert response.json()["first_name"] == "John"
    mock_zep_service.add_user.assert_called_once()


@pytest.mark.asyncio
async def test_create_session(mock_zep_service):
    """Test session creation endpoint"""
    mock_response = SessionResponse(
        session_id="session_123",
        **MOCK_SESSION_DATA
    )
    mock_zep_service.add_session.return_value = mock_response

    response = client.post("/tools/zep/sessions", json=MOCK_SESSION_DATA)
    assert response.status_code == 200
    assert response.json()["session_id"] == "session_123"
    assert response.json()["user_id"] == "john_doe_123"
    mock_zep_service.add_session.assert_called_once()


@pytest.mark.asyncio
async def test_add_memory(mock_zep_service):
    """Test memory addition endpoint"""
    mock_response = MemoryResponse(context="Some context")
    mock_zep_service.add_memory.return_value = mock_response

    response = client.post("/tools/zep/memory", json=MOCK_MEMORY_DATA)
    assert response.status_code == 200
    assert response.json()["context"] == "Some context"
    mock_zep_service.add_memory.assert_called_once()


@pytest.mark.asyncio
async def test_get_user_facts(mock_zep_service):
    """Test getting user facts endpoint"""
    mock_facts = [
        Fact(fact="Fact 1", metadata={"key": "value"}),
        Fact(fact="Fact 2", metadata={"key": "value"})
    ]
    mock_zep_service.get_user_facts.return_value = mock_facts

    response = client.get("/tools/zep/users/john_doe_123/facts")
    assert response.status_code == 200
    assert len(response.json()) == 2
    assert response.json()[0]["fact"] == "Fact 1"
    mock_zep_service.get_user_facts.assert_called_once()


@pytest.mark.asyncio
async def test_get_session_facts(mock_zep_service):
    """Test getting session facts endpoint"""
    mock_facts = [
        Fact(fact="Session Fact 1", metadata={"key": "value"}),
        Fact(fact="Session Fact 2", metadata={"key": "value"})
    ]
    mock_zep_service.get_session_facts.return_value = mock_facts

    response = client.get("/tools/zep/sessions/session_123/facts")
    assert response.status_code == 200
    assert len(response.json()) == 2
    assert response.json()[0]["fact"] == "Session Fact 1"
    mock_zep_service.get_session_facts.assert_called_once()


@pytest.mark.asyncio
async def test_search_user_facts(mock_zep_service):
    """Test searching user facts endpoint"""
    mock_facts = "Fact 1\nFact 2"
    mock_zep_service.search_facts.return_value = mock_facts

    response = client.get("/tools/zep/users/john_doe_123/search-facts?query=test&limit=5")
    assert response.status_code == 200
    assert response.json() == mock_facts
    mock_zep_service.search_facts.assert_called_once()


@pytest.mark.asyncio
async def test_add_graph_data(mock_zep_service):
    """Test adding graph data endpoint"""
    mock_zep_service.add_graph_data.return_value = None

    response = client.post("/tools/zep/graph/data", json=MOCK_GRAPH_DATA)
    assert response.status_code == 200
    assert response.json()["message"] == "Graph data added successfully"
    mock_zep_service.add_graph_data.assert_called_once()


@pytest.mark.asyncio
async def test_search_graph(mock_zep_service):
    """Test graph search endpoint"""
    mock_response = GraphSearchResponse(
        edges=[{"id": "edge1"}],
        nodes=[{"id": "node1"}]
    )
    mock_zep_service.search_graph.return_value = mock_response

    response = client.post("/tools/zep/graph/search", json=MOCK_GRAPH_SEARCH_PARAMS)
    assert response.status_code == 200
    assert len(response.json()["edges"]) == 1
    assert len(response.json()["nodes"]) == 1
    mock_zep_service.search_graph.assert_called_once()


@pytest.mark.asyncio
async def test_create_user_validation():
    """Test user creation input validation"""
    invalid_data = {
        "last_name": "Doe",  # Missing required first_name
        "email": "john@example.com"
    }
    response = client.post("/tools/zep/users", json=invalid_data)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_session_validation():
    """Test session creation input validation"""
    invalid_data = {
        "metadata": {"key": "value"}  # Missing required user_id
    }
    response = client.post("/tools/zep/sessions", json=invalid_data)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_add_memory_validation():
    """Test memory addition input validation"""
    invalid_data = {
        "session_id": "session_123",
        # Missing required chat_history
        "return_context": True
    }
    response = client.post("/tools/zep/memory", json=invalid_data)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_search_graph_validation():
    """Test graph search input validation"""
    invalid_data = {
        "limit": 5,  # Missing required query
        "reranker": "invalid_reranker"  # Invalid reranker value
    }
    response = client.post("/tools/zep/graph/search", json=invalid_data)
    assert response.status_code == 422 
