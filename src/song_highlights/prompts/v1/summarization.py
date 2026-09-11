import json

from pydantic import BaseModel, Field


class ConversationSummary(BaseModel):
    name: str | None = Field(None, description="Nome do usuário")
    age: int | None = Field(None, description="Idade do usuário")
    favorite_genres: list[str] | None = Field(
        None, description="Gêneros musicais favoritos mencionados"
    )
    favorite_bands: list[str] | None = Field(
        None, description="Bandas ou artistas favoritos mencionados"
    )
    key_preferences: str = Field(
        ...,
        description="Sumário conciso das preferências musicais, padrões de humor e hábitos",
    )
    important_context: str | None = Field(
        None, description="Qualquer outro contexto importante sobre o usuário"
    )


def get_summarization_system_prompt() -> str:
    prompt_data = {
        "role": "Sumarizador de conversação para preferências musicais",
        "tarefa": "Analisar conversa e extrair preferências musicais estruturadas",
        "campos_para_extrair": {
            "name": "Nome do usuário",
            "age": "Idade do usuário",
            "favorite_genres": "Todos os gêneros mencionados",
            "favorite_bands": "Todas as bandas/artistas mencionados",
            "key_preferences": "Sumário de 2-4 frases sobre gostos, padrões de humor e contexto de escuta",
            "important_context": "Outros detalhes relevantes",
        },
        "regras": [
            "Combinar informações duplicadas",
            "Ser específico sobre gêneros e artistas",
            (
                "Incluir associações de humor (ex: 'gosta de rock animado ao"
                " fazer exercícios')"
            ),
            (
                "Se atualizando sumário anterior, preservar info não discutida"
                " na nova conversa"
            ),
            "Incluir apenas informações explicitamente declaradas",
        ],
    }
    return json.dumps(prompt_data, ensure_ascii=False)


def get_summarization_user_prompt(
    conversation_history: list[dict],
    previous_summary: ConversationSummary | None = None,
) -> str:
    conversa_str = "\n".join(
        f"{msg['role']}: {msg['content']}" for msg in conversation_history
    )

    summary_dict = previous_summary.model_dump() if previous_summary else "Nenhum"

    prompt_data = {
        "conversa": conversa_str,
        "sumario_anterior": summary_dict,
        "instrucoes": [
            "Atualizar sumário com novas informações desta conversa",
            "Preservar info existente não discutida nas novas mensagens",
        ],
    }
    return json.dumps(prompt_data, ensure_ascii=False)
