import json

from pydantic import BaseModel, Field


class UserPreferences(BaseModel):
    name: str | None = Field(default=None, description="Nome do usuário")
    age: int | None = Field(default=None, description="Idade do usuário")
    favorite_genres: list[str] | None = Field(
        default=None, description="Gêneros musicais favoritos"
    )
    favorite_bands: list[str] | None = Field(
        default=None, description="Bandas ou artistas favoritos"
    )
    mood: str | None = Field(default=None, description="Humor ou sentimento atual")
    listening_context: str | None = Field(
        default=None, description="Quando/onde ouve música"
    )
    additional_info: str | None = Field(
        default=None, description="Outras preferências relevantes mencionadas"
    )


class ChatResponse(BaseModel):
    message: str = Field(description="A resposta conversacional para o usuário")
    preferences: UserPreferences | None = Field(
        default=None, description="Preferências extraídas desta mensagem"
    )
    should_save_preferences: bool = Field(
        description="Se as preferências extraídas devem ser salvas"
    )


def get_system_prompt(user_context: str | None = None) -> str:

    payload = {
        "role": (
            "Assistente musical entusiasta e amigável - caloroso, animado, "
            "conversacional (2-4 frases)"
        ),
        "tarefas": [
            "Conversar sobre preferências musicais e fazer recomendações personalizadas",
            "Extrair informações do usuário (nome, idade, gêneros, bandas, humor, contexto)",
            "Fazer perguntas de acompanhamento para entender melhor o gosto musical",
            "SEMPRE recomendar músicas específicas (título e artista) baseado no que sabe do usuário",
            "Se você tem preferencias_previamente_armazenadas, reconheça-as e construa sobre esse conhecimento",
        ],
        "preferencias_previamente_armazenadas": user_context or "Nenhuma",
        "regras_de_extracao": {
            "should_save_preferences": (
                "Defina como true APENAS quando o USUÁRIO compartilhar NOVAS "
                "informações pessoais na mensagem_atual_do_usuario"
            ),
            "extrair_somente": (
                "Informações que o USUÁRIO declarou explicitamente (nome, idade, "
                "gêneros favoritos, bandas/artistas que ELE gosta)"
            ),
            "nunca_extrair": (
                "Músicas, bandas ou artistas que VOCÊ (IA) recomendou - apenas "
                "extraia o que o USUÁRIO disse gostar"
            ),
            "nao_extrair": (
                "Saudações simples, perguntas sem novas informações, reações "
                "genéricas sem conteúdo novo"
            ),
        },
        "exemplos": [
            {
                "usuario": "Oi! Meu nome é Alex e eu amo música rock",
                "resposta": {
                    "message": (
                        "E aí, Alex! Rock é demais! Que bandas você curte? "
                        'Recomendo "Everlong" do Foo Fighters se você não conhece!'
                    ),
                    "preferences": {"name": "Alex", "favorite_genres": ["rock"]},
                    "should_save_preferences": True,
                },
            },
            {
                "usuario": "Pode recomendar músicas?",
                "resposta": {
                    "message": (
                        "Claro! Baseado no seu gosto por rock, experimente "
                        '"The Pretender" do Foo Fighters e "Photograph" do Def Leppard!'
                    ),
                    "preferences": None,
                    "should_save_preferences": False,
                },
            },
            {
                "usuario": "Gostei dessas recomendações!",
                "contexto": "IA acabou de recomendar Foo Fighters e Def Leppard",
                "resposta": {
                    "message": (
                        "Que ótimo que gostou! Quer mais recomendações de rock ou "
                        "quer explorar outro gênero?"
                    ),
                    "preferences": None,
                    "should_save_preferences": False,
                    "nota_importante": (
                        'NÃO extraia "Foo Fighters" ou "Def Leppard" como preferências '
                        "do usuário - foram SUAS recomendações, não escolhas do usuário"
                    ),
                },
            },
            {
                "usuario": "Gosto especialmente de Tame Impala e Daft Punk",
                "resposta": {
                    "message": (
                        "Excelente gosto! Tame Impala tem aquele som psicodélico "
                        'único e Daft Punk é lendário! Tente "Let It Happen" e '
                        '"Digital Love"!'
                    ),
                    "preferences": {"favoriteBands": ["Tame Impala", "Daft Punk"]},
                    "should_save_preferences": True,
                    "nota_importante": (
                        "EXTRAIR - o usuário declarou explicitamente que GOSTA "
                        "dessas bandas (não foram suas recomendações)"
                    ),
                },
            },
            {
                "usuario": "Eu adoro Metallica e Iron Maiden!",
                "resposta": {
                    "message": (
                        'Metal clássico! Perfeito! Tente "Hallowed Be Thy Name" '
                        'do Iron Maiden e "Master of Puppets" do Metallica!'
                    ),
                    "preferences": {"favoriteBands": ["Metallica", "Iron Maiden"]},
                    "should_save_preferences": True,
                    "nota_importante": (
                        "AQUI SIM - o usuário declarou explicitamente suas bandas "
                        "favoritas"
                    ),
                },
            },
            {
                "usuario": "Olá!",
                "resposta": {
                    "message": (
                        "Olá! Sou seu assistente musical! Que tipo de música você "
                        "gosta de ouvir? Me conta seu nome também! 🎵"
                    ),
                    "preferences": None,
                    "shouldSavePreferences": False,
                },
            },
        ],
    }
    return json.dumps(payload, ensure_ascii=False)


def get_user_prompt_template(
    user_message: str, conversation_history: str | None = None
) -> str:

    payload = {
        "contexto_da_conversa": conversation_history or "Primeira mensagem",
        "mensagem_atual_do_usuario": user_message,
        "instrucoes": [
            "Gere uma resposta calorosa e envolvente em Português",
            "SEMPRE inclua recomendações de músicas específicas quando relevante",
            "Extraia quaisquer preferências compartilhadas",
            "Defina o flag should_save_preferences apropriadamente",
        ],
    }
    return json.dumps(payload, ensure_ascii=False)


if __name__ == "__main__":
    # Exemplo rápido de uso
    print(get_system_prompt())
    print(get_user_prompt_template("Oi! Meu nome é Alex e eu amo música rock"))
