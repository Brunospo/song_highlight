from langgraph.graph import END, START, StateGraph

from song_highlights.graph.graph_state import GraphState
from song_highlights.graph.nodes.chat_node import create_chat_node
from song_highlights.graph.nodes.conditional_node import (
    route_after_chat,
    route_after_save_preferences,
)
from song_highlights.graph.nodes.save_preferences_node import (
    create_save_preferences_node,
)
from song_highlights.graph.nodes.summarization_node import create_summarization_node
from song_highlights.services.memory_service import MemoryService
from song_highlights.services.open_router_service import OpenRouterService
from song_highlights.services.preferences_service import PreferencesService


def build_chat_graph(
    llm_client: OpenRouterService,
    preferences_service: PreferencesService,
    memory_service: MemoryService,
):
    workflow = StateGraph(GraphState)

    workflow.add_node("chat", create_chat_node(llm_client, preferences_service))
    workflow.add_node(
        "save_preferences", create_save_preferences_node(preferences_service)
    )
    workflow.add_node(
        "summarize", create_summarization_node(llm_client, preferences_service)
    )

    workflow.add_edge(START, "chat")
    workflow.add_conditional_edges(
        "chat",
        route_after_chat,
        {"save_preferences": "save_preferences", "summarize": "summarize", "end": END},
    )

    workflow.add_conditional_edges(
        "save_preferences",
        route_after_save_preferences,
        {"summarize": "summarize", "end": END},
    )

    workflow.add_edge("summarize", END)

    return workflow.compile(
        checkpointer=memory_service["checkpointer"], store=memory_service["store"]
    )
