from langchain.messages import HumanMessage, RemoveMessage
from langchain_core.runnables import RunnableConfig

from song_highlights.graph.graph_state import GraphState
from song_highlights.prompts.v1.summarization import (
    ConversationSummary,
    get_summarization_system_prompt,
    get_summarization_user_prompt,
)
from song_highlights.services.open_router_service import OpenRouterService
from song_highlights.services.preferences_service import PreferencesService


def create_summarization_node(
    llm_client: OpenRouterService, preferences_service: PreferencesService
):
    async def summarization_node(
        state: GraphState, config: RunnableConfig | None
    ) -> dict:

        conversation_history = [
            {
                "role": "User" if isinstance(msg, HumanMessage) else "AI",
                "content": msg.content,
            }
            for msg in state["messages"]
        ]

        previous_summary: ConversationSummary | None = state.get("conversation_summary")
        system_prompt = get_summarization_system_prompt()
        user_prompt = get_summarization_user_prompt(
            conversation_history, previous_summary
        )

        result = await llm_client.generate_structured(
            system_prompt, user_prompt, ConversationSummary
        )

        if result.get("error") or not result.get("data"):
            print(f"❌ Falha ao sumarizar conversa: {result.get('error')}")

            return {"needs_summarization": False}

        user_id = (
            config["configurable"]["context"]["user_id"]
            or state["user_id"]
            or "unknown"
        )

        summary_dict = result["data"].model_dump()
        await preferences_service.store_summary(user_id, summary_dict)

        delete_messages = [RemoveMessage(id=m.id) for m in state["messages"][:-2]]

        return {
            "messages": delete_messages,
            "conversation_summary": result["data"],
            "needs_summarization": False,
        }

    return summarization_node
