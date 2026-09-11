from dataclasses import asdict
from typing import TypeVar

from langchain.agents import create_agent
from langchain.agents.structured_output import ProviderStrategy
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from pydantic import BaseModel

from song_highlights.config import ModelConfig, config

T = TypeVar("T", bound=BaseModel)


class OpenRouterService:
    __config: ModelConfig
    __llm_client: ChatOpenAI

    def __init__(self, config_override: ModelConfig | None = None) -> None:
        self.__config = config_override or config

        self.__llm_client = ChatOpenAI(
            model=self.__config.models[0],
            temperature=self.__config.temperature,
            openai_api_key=self.__config.api_key,
            openai_api_base="https://openrouter.ai/api/v1",
            default_headers={
                "HTTP-Referer": self.__config.http_referer,
                "X-Title": self.__config.x_title,
            },
            extra_body={"provider": asdict(self.__config.provider)},
        )

    async def generate_structured(
        self, system_prompt: str, user_prompt: str, schema: type[T]
    ):
        try:
            agent = create_agent(
                model=self.__llm_client,
                tools=[],
                response_format=ProviderStrategy(schema),
            )

            messages = [SystemMessage(system_prompt), HumanMessage(user_prompt)]

            data = await agent.ainvoke({"messages": messages})

            return {"success": True, "data": data["structured_response"]}

        except Exception as error:
            print(f"Error OpenRouterService: {error}")

            return {"success": False, "error": str(error)}
