from song_highlights.graph.graph_state import GraphState
from song_highlights.services.open_router_service import OpenRouterService


def create_summarization_node(llm_client: OpenRouterService):
    async def summarization_node(state: GraphState) -> dict:
        return {**state}

    return summarization_node
