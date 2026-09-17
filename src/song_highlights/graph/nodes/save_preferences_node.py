from langchain_core.runnables import RunnableConfig

from song_highlights.graph.graph_state import GraphState
from song_highlights.services.preferences_service import PreferencesService


def create_save_preferences_node(preferences_service: PreferencesService):
    async def save_preferences_node(
        state: GraphState, config: RunnableConfig | None
    ) -> dict:

        if not state["extracted_preferences"]:
            return {}

        user_id = (
            config["configurable"]["context"]["user_id"]
            or state["user_id"]
            or "unknown"
        )
        user_prefs = state["extracted_preferences"].model_dump()

        await preferences_service.merge_preferences(user_id, user_prefs)

        return {"extracted_preferences": None}

    return save_preferences_node
