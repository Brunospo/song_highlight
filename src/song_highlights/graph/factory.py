from song_highlights.config import config
from song_highlights.graph.graph import build_chat_graph
from song_highlights.services.memory_service import create_memory_service
from song_highlights.services.open_router_service import OpenRouterService
from song_highlights.services.preferences_service import PreferencesService


async def build_graph(db_path: str = "./preferences.db"):
    llm_client = OpenRouterService(config)

    memory_service = await create_memory_service()
    preferences_service = PreferencesService(db_path)

    graph_obj = build_chat_graph(llm_client, preferences_service, memory_service)

    return {
        "graph": graph_obj,
        "preferences_service": preferences_service,  # Esse preferene dá erro na UI do langgraph, tenho que remover ele e instanciar em seu próprio módulo.
    }


async def graph():
    return await build_graph()
