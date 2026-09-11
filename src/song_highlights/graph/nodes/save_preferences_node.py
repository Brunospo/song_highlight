from langchain_core.runnables import RunnableConfig

from song_highlights.graph.graph_state import GraphState


def create_save_preferences_node():
    async def save_preferences_node(
        state: GraphState, config: RunnableConfig | None
    ) -> dict:
        return {**state}

    return save_preferences_node
