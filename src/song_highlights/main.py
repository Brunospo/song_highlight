import asyncio
import sys

from langchain_core.messages import HumanMessage

from song_highlights.graph.factory import build_graph
from song_highlights.services.preferences_service import PreferencesService


def parse_args() -> dict[str, str]:
    args = sys.argv[1:]

    try:
        user_index = args.index("--user")

        if user_index + 1 < len(args):
            return {"user_id": args[user_index + 1]}
    except ValueError:
        pass

    return {}


async def async_main():
    try:
        print("═" * 60)
        print("  🎵 Recomendador de Músicas com Memória (LangGraph)")
        print("═" * 60)
        print('\nDigite suas mensagens abaixo. Digite "exit" para sair.\n')

        graph_data = await build_graph()
        graph = graph_data["graph"]
        preferences_service: PreferencesService = graph_data["preferences_service"]

        args = parse_args()
        user_id = args.get("user_id")
        actual_user_id = user_id or "anonymous"

        thread_id = f"{actual_user_id}-{int(asyncio.get_running_loop().time() * 1000)}"

        config = {
            "configurable": {"thread_id": thread_id},
            "context": {"user_id": actual_user_id},
        }

        print(f"👤 Usuário: {actual_user_id}")
        print(f"📝 ID da Sessão: {thread_id}\n")

        user_context = await preferences_service.get_basic_info(actual_user_id)

        if user_context:
            print(f"📚 Informações do usuário carregadas:\n{user_context}\n")

        try:
            initial_message = (
                "Inicie a conversa de forma casual mencionando o que você sabe sobre mim e recomende uma música!"
                if user_context
                else "Olá! Me apresente de forma amigável e pergunte sobre meu nome e preferências musicais."
            )

            result = await graph.ainvoke(
                {
                    "messages": [HumanMessage(content=initial_message)],
                    "user_context": user_context,
                    "user_id": thread_id,
                },
                config,
            )

            greeting = result["messages"][-1]
            print(f"AI: {greeting.content}\n")
        except Exception as error:
            print(f"❌ Erro ao iniciar conversa: {error}")

        while True:
            user_input = input("Você: ")

            if not user_input.strip():
                continue
            if user_input.strip().lower() == "exit":
                print("\n👋 Até mais!\n")
                break

            try:
                result = await graph.ainvoke(
                    {
                        "messages": [HumanMessage(content=user_input)],
                        "user_id": thread_id,
                    },
                    config,
                )

                last_message = result["messages"][-1]
                print(f"\nAI: {last_message.content}\n")

            except Exception as error:
                print(f"\n❌ Erro ao gerar resposta: {error}")
                print("AI: Desculpe, encontrei um erro. Pode tentar novamente?\n")

    except Exception as error:
        print(f"\n❌ Erro fatal: {error}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


def main():
    """Função síncrona que o UV vai chamar ao executar 'song_highlights'."""
    asyncio.run(async_main())


if __name__ == "__main__":
    main()
