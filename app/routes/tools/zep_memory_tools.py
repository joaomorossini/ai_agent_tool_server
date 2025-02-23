
import os
import uuid
import rich
from typing import Optional
from dotenv import load_dotenv
from zep_cloud.client import Zep
from zep_cloud import Message
from langchain.tools import BaseTool, tool

load_dotenv()


def add_user(
    first_name: str,
    last_name: Optional[str] = None,
    email: Optional[str] = None,
    metadata: Optional[dict] = None,
) -> str:
    """
    Adds a new user to the Zep client.

    Args:
        first_name (str): The first name of the user.
        last_name (Optional[str]): The last name of the user.
        email (Optional[str]): The email of the user.
        metadata (Optional[dict]): The metadata associated with the user.

    Returns:
        str: The generated user ID.
    """

    client = Zep(
        api_key=os.getenv("ZEP_CLOUD_API_KEY"),
    )
    user_id = f"{first_name.lower()}_{last_name.lower() if last_name else ''}_{str(uuid.uuid4())[:20]}"

    user_data = client.user.add(
        user_id=user_id,
        email=email,
        first_name=first_name,
        last_name=last_name,
        metadata=metadata,
    )
    return user_data

class ZepUtils:

    def __init__(self):
        self.client = AsyncZep(
            api_key=os.getenv("ZEP_CLOUD_API_KEY"),
        )

    async def add_user(
        self,
        first_name: str,
        last_name: Optional[str] = None,
        email: Optional[str] = None,
        metadata: Optional[dict] = None,
    ) -> str:
        """
        Adds a new user to the Zep client.

        Args:
            first_name (str): The first name of the user.
            last_name (Optional[str]): The last name of the user.
            email (Optional[str]): The email of the user.
            metadata (Optional[dict]): The metadata associated with the user.

        Returns:
            str: The generated user ID.
        """
        user_id = f"{first_name.lower()}_{last_name.lower() if last_name else ''}_{str(uuid.uuid4())[:20]}"

        user_data = await self.client.user.add(
            user_id=user_id,
            email=email,
            first_name=first_name,
            last_name=last_name,
            metadata=metadata,
        )
        return user_data

    async def add_session(self, user_id: str, metadata: Optional[dict] = None) -> dict:
        """
        Adds a new session for a given user to the Zep client.

        Args:
            user_id (str): The ID of the user.
            metadata (Optional[dict]): The metadata associated with the session.

        Returns:
            dict: The response from the Zep client containing session details.
        """
        session_id = str(uuid.uuid4())
        response = await self.client.memory.add_session(
            user_id=user_id,
            session_id=session_id,
            metadata=metadata,
        )
        return response

    # TODO: Confirm correct format for the chat_history
    def _convert_to_zep_messages(self, chat_history: list[dict[str, str | None]]) -> list[Message]:
        """
        Converts a list of chat history dictionaries to a list of Zep Message objects.

        Args:
            chat_history (list[dict[str, str | None]]): A list of dictionaries representing chat history.
                Each dictionary should have keys like "role", "content", and optionally "name".

        Returns:
            list[Message]: A list of Zep Message objects.
        """
        return [
            Message(
                role_type=msg["role"],
                role=msg.get("name", None),
                content=msg["content"],
            )
            for msg in chat_history
        ]

    async def add_memory_to_session(self, session_id: str, chat_history: list[dict[str, str | None]], return_context: bool = False) -> Optional[str]:
        """
        Adds messages to the Zep memory for a given session.

        Args:
            session_id (str): The ID of the session to add messages to.
            chat_history (list[dict[str, str | None]]): A list of dictionaries representing chat history.
                Each dictionary should have keys like "role", "content", and optionally "name".
            return_context (bool): Whether to return memory context relevant to the most recent messages.

        Returns:
            Optional[str]: The memory context if return_context is True, otherwise None.
        """
        formatted_chat_messages = self._convert_to_zep_messages(chat_history)
        response = await self.client.memory.add(
            session_id=session_id, 
            messages=formatted_chat_messages,
            return_context=return_context
        )
        return response.context if return_context else None

    async def get_user_facts(self, user_id: str, verbose: bool = False):
        """
        Gets facts for a given user.

        Args:
            user_id (str): The ID of the user to get facts for.

        Returns:
            list[dict[str, str]]: A list of dictionaries representing facts.
        """
        user_facts_response = await self.client.user.get_facts(user_id=user_id)
        if verbose:
            for fact in user_facts_response.facts:
                rich.print(fact)
        return user_facts_response.facts

    async def get_session_facts(self, session_id: str, verbose: bool = False):
        """
        Gets facts for a given session.

        Args:
            session_id (str): The ID of the session to get facts for.

        Returns:
            list[dict[str, str]]: A list of dictionaries representing session facts.
        """
        session_facts_response = await self.client.memory.get(session_id=session_id)
        if session_facts_response and session_facts_response.relevant_facts:
            if verbose:
                for fact in session_facts_response.relevant_facts:
                    rich.print(fact)
            return session_facts_response.facts
        else:
            return []

    async def search_facts(self, user_id: str, query: str, limit: int = 5):
        """Search for facts in all conversations had with a user.
        
        Args:
            state (dict): The Agent's state, which should contain 'user_name'.
            query (str): The search query.
            limit (int): The number of results to return. Defaults to 5.
        Returns:
            list: A list of facts that match the search query.
        """
        relevant_facts = await self.client.memory.search_sessions(
          user_id=user_id, 
          text=query, 
          limit=limit, 
          search_scope="facts"
        )

        formatted_relevant_facts = ""

        for fact in relevant_facts.results:
            formatted_relevant_facts =+ f"{fact.fact}\n"

        return formatted_relevant_facts

    async def add_data_to_graph(
        self, data: dict, group_id: str = None, data_type: str = None, user_id: str = None
    ):
        """
        Adds data to the Zep graph.

        Args:
            data (dict): Data to add to the graph.
            group_id (str, optional): Group ID for the data. Defaults to None.
            data_type (str, optional): Type of data (text, json, message). Defaults to None.
            user_id (str, optional): User ID associated with the data. Defaults to None.

        Returns:
            None: This method does not return any value.
        """
        await self.client.graph.add(data=data, group_id=group_id, type=data_type, user_id=user_id)

    async def search_graph(
        self,
        query: str,
        center_node_uuid: str = None,
        group_id: str = None,
        limit: int = 5,
        mmr_lambda: float = None,
        reranker: str = "rrf",
        scope: str = "edges",
        user_id: str = None,
    ):
        """
        Searches the Zep graph based on the provided query and parameters.

        Args:
            query (str): The string to search for (required).
            center_node_uuid (str, optional): Node UUID to rerank around for node distance reranking. Defaults to None.
            group_id (str, optional): Group ID to search within. One of user_id or group_id must be provided. Defaults to None.
            limit (int, optional): The maximum number of results to retrieve. Defaults to 10, limited to 50.
            mmr_lambda (float, optional): Weighting for maximal marginal relevance. Defaults to None.
            reranker (str, optional): Reranker algorithm to use. Defaults to "rrf". Allowed values: "rrf", "mmr", "node_distance", "episode_mentions", "cross_encoder".
            scope (str, optional): Scope of the search. Defaults to "edges". Allowed values: "edges", "nodes".
            user_id (str, optional): User ID to search within. One of user_id or group_id must be provided. Defaults to None.

        Returns:
            dict: A dictionary containing the graph search results, including 'edges' and 'nodes'.
        """
        search_params = {"query": query}
        if center_node_uuid:
            search_params["center_node_uuid"] = center_node_uuid
        if group_id:
            search_params["group_id"] = group_id
        if limit:
            search_params["limit"] = limit
        if mmr_lambda:
            search_params["mmr_lambda"] = mmr_lambda
        if reranker:
            search_params["reranker"] = reranker
        if scope:
            search_params["scope"] = scope
        if user_id:
            search_params["user_id"] = user_id

        search_response = await self.client.graph.search(**search_params)
        return search_response

