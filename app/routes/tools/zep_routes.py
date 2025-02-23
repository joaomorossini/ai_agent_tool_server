from typing import List
from fastapi import APIRouter, Depends, HTTPException
from app.services.zep_service import ZepService
from app.models.zep_models import (
    UserBase, UserResponse, SessionCreate, SessionResponse,
    MemoryAdd, MemoryResponse, GraphData, GraphSearchParams,
    GraphSearchResponse, Fact
)

router = APIRouter(prefix="/tools/zep", tags=["zep"])


async def get_zep_service() -> ZepService:
    """Dependency to get ZepService instance"""
    try:
        return ZepService()
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/users", response_model=UserResponse)
async def create_user(
    user_data: UserBase,
    zep_service: ZepService = Depends(get_zep_service)
) -> UserResponse:
    """Create a new user in Zep"""
    return await zep_service.add_user(user_data)


@router.post("/sessions", response_model=SessionResponse)
async def create_session(
    session_data: SessionCreate,
    zep_service: ZepService = Depends(get_zep_service)
) -> SessionResponse:
    """Create a new session for a user"""
    return await zep_service.add_session(session_data)


@router.post("/memory", response_model=MemoryResponse)
async def add_memory(
    memory_data: MemoryAdd,
    zep_service: ZepService = Depends(get_zep_service)
) -> MemoryResponse:
    """Add memory to a session"""
    return await zep_service.add_memory(memory_data)


@router.get("/users/{user_id}/facts", response_model=List[Fact])
async def get_user_facts(
    user_id: str,
    zep_service: ZepService = Depends(get_zep_service)
) -> List[Fact]:
    """Get facts for a user"""
    return await zep_service.get_user_facts(user_id)


@router.get("/sessions/{session_id}/facts", response_model=List[Fact])
async def get_session_facts(
    session_id: str,
    zep_service: ZepService = Depends(get_zep_service)
) -> List[Fact]:
    """Get facts for a session"""
    return await zep_service.get_session_facts(session_id)


@router.get("/users/{user_id}/search-facts")
async def search_user_facts(
    user_id: str,
    query: str,
    limit: int = 5,
    zep_service: ZepService = Depends(get_zep_service)
) -> str:
    """Search for facts in user conversations"""
    return await zep_service.search_facts(user_id, query, limit)


@router.post("/graph/data")
async def add_graph_data(
    graph_data: GraphData,
    zep_service: ZepService = Depends(get_zep_service)
) -> None:
    """Add data to the graph"""
    await zep_service.add_graph_data(graph_data)
    return {"message": "Graph data added successfully"}


@router.post("/graph/search", response_model=GraphSearchResponse)
async def search_graph(
    search_params: GraphSearchParams,
    zep_service: ZepService = Depends(get_zep_service)
) -> GraphSearchResponse:
    """Search the graph"""
    return await zep_service.search_graph(search_params) 
