from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class UserBase(BaseModel):
    """Base model for user data"""
    first_name: str
    last_name: Optional[str] = None
    email: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class UserResponse(UserBase):
    """Response model for user operations"""
    user_id: str


class SessionCreate(BaseModel):
    """Model for creating a new session"""
    user_id: str
    metadata: Optional[Dict[str, Any]] = None


class SessionResponse(BaseModel):
    """Response model for session operations"""
    session_id: str
    user_id: str
    metadata: Optional[Dict[str, Any]] = None


class Message(BaseModel):
    """Model for chat messages"""
    role: str
    content: str
    name: Optional[str] = None


class MemoryAdd(BaseModel):
    """Model for adding memory to a session"""
    session_id: str
    chat_history: List[Dict[str, Optional[str]]]
    return_context: bool = False


class MemoryResponse(BaseModel):
    """Response model for memory operations"""
    context: Optional[str] = None


class Fact(BaseModel):
    """Model for facts"""
    fact: str
    metadata: Optional[Dict[str, Any]] = None


class GraphData(BaseModel):
    """Model for graph data"""
    data: Dict[str, Any]
    group_id: Optional[str] = None
    data_type: Optional[str] = None
    user_id: Optional[str] = None


class GraphSearchParams(BaseModel):
    """Parameters for graph search"""
    query: str
    center_node_uuid: Optional[str] = None
    group_id: Optional[str] = None
    limit: int = Field(default=5, le=50)
    mmr_lambda: Optional[float] = None
    reranker: str = Field(default="rrf", pattern="^(rrf|mmr|node_distance|episode_mentions|cross_encoder)$")
    scope: str = Field(default="edges", pattern="^(edges|nodes)$")
    user_id: Optional[str] = None


class GraphSearchResponse(BaseModel):
    """Response model for graph search"""
    edges: List[Dict[str, Any]]
    nodes: List[Dict[str, Any]] 
