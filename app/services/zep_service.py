import os
import uuid
from typing import Optional, List, Dict, Any
from dotenv import load_dotenv
from zep_cloud.client import AsyncZep
from zep_cloud import Message
from fastapi import HTTPException

from app.models.zep_models import (
    UserBase, UserResponse, SessionCreate, SessionResponse,
    MemoryAdd, MemoryResponse, GraphData, GraphSearchParams,
    GraphSearchResponse, Fact
)

load_dotenv()


class ZepService:
    """Service class for handling Zep operations"""

    def __init__(self):
        api_key = os.getenv("ZEP_CLOUD_API_KEY")
        if not api_key:
            raise ValueError("ZEP_CLOUD_API_KEY environment variable not set")
        self.client = AsyncZep(api_key=api_key)

    async def add_user(self, user_data: UserBase) -> UserResponse:
        """Add a new user to Zep"""
        try:
            user_id = f"{user_data.first_name.lower()}_{user_data.last_name.lower() if user_data.last_name else ''}_{str(uuid.uuid4())[:20]}"
            
            response = await self.client.user.add(
                user_id=user_id,
                email=user_data.email,
                first_name=user_data.first_name,
                last_name=user_data.last_name,
                metadata=user_data.metadata,
            )
            
            return UserResponse(
                user_id=user_id,
                first_name=user_data.first_name,
                last_name=user_data.last_name,
                email=user_data.email,
                metadata=user_data.metadata
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to add user: {str(e)}")

    async def add_session(self, session_data: SessionCreate) -> SessionResponse:
        """Add a new session for a user"""
        try:
            session_id = str(uuid.uuid4())
            response = await self.client.memory.add_session(
                user_id=session_data.user_id,
                session_id=session_id,
                metadata=session_data.metadata,
            )
            
            return SessionResponse(
                session_id=session_id,
                user_id=session_data.user_id,
                metadata=session_data.metadata
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to add session: {str(e)}")

    def _convert_to_zep_messages(self, chat_history: List[Dict[str, Optional[str]]]) -> List[Message]:
        """Convert chat history to Zep Message format"""
        return [
            Message(
                role_type=msg["role"],
                role=msg.get("name"),
                content=msg["content"],
            )
            for msg in chat_history
        ]

    async def add_memory(self, memory_data: MemoryAdd) -> MemoryResponse:
        """Add memory to a session"""
        try:
            formatted_messages = self._convert_to_zep_messages(memory_data.chat_history)
            response = await self.client.memory.add(
                session_id=memory_data.session_id,
                messages=formatted_messages,
                return_context=memory_data.return_context
            )
            
            return MemoryResponse(context=response.context if memory_data.return_context else None)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to add memory: {str(e)}")

    async def get_user_facts(self, user_id: str) -> List[Fact]:
        """Get facts for a user"""
        try:
            response = await self.client.user.get_facts(user_id=user_id)
            return [Fact(fact=fact.fact, metadata=fact.metadata) for fact in response.facts]
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to get user facts: {str(e)}")

    async def get_session_facts(self, session_id: str) -> List[Fact]:
        """Get facts for a session"""
        try:
            response = await self.client.memory.get(session_id=session_id)
            if response and response.relevant_facts:
                return [Fact(fact=fact.fact, metadata=fact.metadata) for fact in response.facts]
            return []
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to get session facts: {str(e)}")

    async def search_facts(self, user_id: str, query: str, limit: int = 5) -> str:
        """Search for facts in user conversations"""
        try:
            response = await self.client.memory.search_sessions(
                user_id=user_id,
                text=query,
                limit=limit,
                search_scope="facts"
            )
            
            formatted_facts = "\n".join(fact.fact for fact in response.results)
            return formatted_facts
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to search facts: {str(e)}")

    async def add_graph_data(self, graph_data: GraphData) -> None:
        """Add data to the graph"""
        try:
            await self.client.graph.add(
                data=graph_data.data,
                group_id=graph_data.group_id,
                type=graph_data.data_type,
                user_id=graph_data.user_id
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to add graph data: {str(e)}")

    async def search_graph(self, search_params: GraphSearchParams) -> GraphSearchResponse:
        """Search the graph"""
        try:
            search_response = await self.client.graph.search(
                query=search_params.query,
                center_node_uuid=search_params.center_node_uuid,
                group_id=search_params.group_id,
                limit=search_params.limit,
                mmr_lambda=search_params.mmr_lambda,
                reranker=search_params.reranker,
                scope=search_params.scope,
                user_id=search_params.user_id
            )
            
            return GraphSearchResponse(
                edges=search_response.edges,
                nodes=search_response.nodes
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to search graph: {str(e)}") 
