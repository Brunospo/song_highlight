from typing import Literal

from song_highlights.graph.graph_state import GraphState


def route_after_chat(
    state: GraphState,
) -> Literal["save_preferences", "summarize", "end"]:
    if state.get("extracted_preferences"):
        return "save_preferences"
    elif state.get("needs_summarization"):
        return "summarize"
    return "end"


def route_after_save_preferences(
    state: GraphState,
) -> Literal["summarize", "end"]:
    if state.get("needs_summarization"):
        return "summarize"
    return "end"
