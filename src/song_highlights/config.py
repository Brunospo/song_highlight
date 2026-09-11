import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("OPENROUTER_API_KEY")
assert api_key, "OPENROUTER_API_KEY is not set in environment variables"


@dataclass
class ProviderSortConfig:
    by: str
    partition: str


@dataclass
class ProviderConfig:
    sort: ProviderSortConfig


@dataclass
class ModelConfig:
    api_key: str
    http_referer: str
    x_title: str
    provider: ProviderConfig
    models: list[str]
    temperature: float


# Instanciando a configuração
config = ModelConfig(
    api_key=api_key,
    http_referer="",
    x_title="IA Devs - Prompt Chaining Article Generator",
    models=["nvidia/nemotron-3-ultra-550b-a55b:free"],
    provider=ProviderConfig(
        sort=ProviderSortConfig(
            by="throughput",
            partition="none",
        )
    ),
    temperature=0.7,
)
