from langchain.messages import AIMessage, HumanMessage
from langchain_core.runnables import RunnableConfig

from song_highlights.graph.graph_state import GraphState
from song_highlights.prompts.v1.chat_response import (
    ChatResponse,
    get_system_prompt,
    get_user_prompt_template,
)
from song_highlights.services.open_router_service import OpenRouterService
from song_highlights.services.preferences_service import PreferencesService


def create_chat_node(
    llm_client: OpenRouterService, preferences_service: PreferencesService
):
    async def chat_node(state: GraphState, config: RunnableConfig | None) -> dict:
        user_id = (
            config["configurable"]["context"]["user_id"]
            or state["user_id"]
            or "unknown"
        )
        user_context = state[
            "user_context"
        ] or await preferences_service.get_basic_info(user_id)
        system_prompt = get_system_prompt(user_context)

        conversation_history = "\n".join(
            f"{'User' if isinstance(msg, HumanMessage) else 'AI'}: {msg.content}"
            for msg in state["messages"]
        )

        user_message = state["messages"][-1].content

        user_prompt = get_user_prompt_template(user_message, conversation_history)

        result = await llm_client.generate_structured(
            system_prompt, user_prompt, ChatResponse
        )

        if not result or not result["data"]:
            print("❌ Falha ao gerar resposta:", result["error"])
            return {
                "messages": [
                    AIMessage("Desculpe, encontrei um erro. Pode tentar novamente? ")
                ]
            }

        response = result["data"]

        return {
            "messages": [AIMessage(response.message)],
            "extracted_preferences": response.preferences
            if response.should_save_preferences
            else None,
            "needs_summarization": False,
        }

    return chat_node
