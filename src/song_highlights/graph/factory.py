from song_highlights.config import config
from song_highlights.graph.graph import build_chat_graph
from song_highlights.services.open_router_service import OpenRouterService


async def build_graph():
    llm_client = OpenRouterService(config)

    graph_obj = build_chat_graph(llm_client)

    async def mock_search(*args, **kwargs):
        return []

    return {"graph": graph_obj, "memory_service": {"store": {"search": mock_search}}}


async def graph():
    return await build_graph()
