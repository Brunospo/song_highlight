from collections.abc import Sequence
from typing import Annotated, Any, TypedDict

from langchain_core.messages import BaseMessage
from langgraph.graph import add_messages


class GraphState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]

    user_context: str | None
    extracted_preferences: Any | None
    needs_summarization: bool | None
    conversation_summary: Any | None
    user_id: str | None
