from langchain_core.runnables import RunnableConfig

from song_highlights.graph.graph_state import GraphState
from song_highlights.services.open_router_service import OpenRouterService


def create_chat_node(llm_client: OpenRouterService):
    async def chat_node(state: GraphState, config: RunnableConfig | None) -> dict:
        return {**state}

    return chat_node
