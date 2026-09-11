import asyncio
import os
import time

import pytest
import pytest_asyncio
from langchain_core.messages import HumanMessage

from song_highlights.graph.factory import build_graph

TEST_DB_PATH = "./test-memory.db"


@pytest.fixture(autouse=True)
def setup_teardown():
    """Executado antes e depois de cada teste para limpar o banco de dados."""
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)
    yield
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)


@pytest_asyncio.fixture
async def graph_setup():
    """Constrói o grafo e o serviço de memória de forma assíncrona."""
    built = await build_graph()
    return built["graph"], built["memory_service"]


@pytest.mark.asyncio
async def test_deve_extrair_e_salvar_preferencias_do_usuario(graph_setup):
    graph, memory_service = graph_setup
    test_thread_id = f"test-user-{int(time.time() * 1000)}"
    config = {
        "configurable": {"thread_id": test_thread_id},
        "context": {"userId": test_thread_id},
    }

    response = await graph.ainvoke(
        {
            "messages": [
                HumanMessage(content="Oi! Meu nome é Alex e eu amo rock e metal")
            ],
            "userId": test_thread_id,
        },
        config,
    )

    assert len(response["messages"]) > 0, "Deve ter mensagens de resposta"

    last_message = response["messages"][-1]
    assert last_message.type == "ai", "Última mensagem deve ser da IA"

    content = last_message.content.lower()
    assert "alex" in content or "rock" in content or "metal" in content, (
        "Resposta deve reconhecer as preferências"
    )

    await asyncio.sleep(0.5)

    namespace = ["memories", test_thread_id]
    # Adicionado o 'await' já que mock_search é async def no factory
    saved_memories = await memory_service["store"]["search"](namespace, limit=10)

    assert len(saved_memories) > 0, "Preferências devem estar salvas"

    memories_text = " ".join(
        [m.get("value", {}).get("data", "") for m in saved_memories]
    )
    assert "Alex" in memories_text, "Nome deve estar salvo"


@pytest.mark.asyncio
async def test_deve_manter_multiplas_trocas_e_fazer_sumarizacao(graph_setup):
    graph, memory_service = graph_setup
    test_thread_id = f"test-user-{int(time.time() * 1000)}"
    config = {
        "configurable": {"thread_id": test_thread_id},
        "context": {"userId": test_thread_id},
    }

    await graph.ainvoke(
        {
            "messages": [
                HumanMessage(content="Oi! Sou a Sarah e adoro indie e eletrônica")
            ],
            "userId": test_thread_id,
        },
        config,
    )

    await graph.ainvoke(
        {
            "messages": [
                HumanMessage(content="Gosto especialmente de Tame Impala e Daft Punk")
            ],
            "userId": test_thread_id,
        },
        config,
    )

    await asyncio.sleep(0.5)

    namespace = ["memories", test_thread_id]
    saved_memories = await memory_service["store"]["search"](namespace, limit=10)

    assert len(saved_memories) > 0, "Memórias devem existir"

    memories_text = " ".join(
        [m.get("value", {}).get("data", "").lower() for m in saved_memories]
    )
    assert "sarah" in memories_text, "Nome deve estar salvo"
    assert (
        "indie" in memories_text
        or "eletrônica" in memories_text
        or "electronic" in memories_text
    ), "Gêneros devem estar salvos"


@pytest.mark.asyncio
async def test_deve_recuperar_contexto_em_nova_sessao(graph_setup):
    graph, memory_service = graph_setup
    test_thread_id = f"test-user-{int(time.time() * 1000)}"
    config = {
        "configurable": {"thread_id": test_thread_id},
        "context": {"userId": test_thread_id},
    }

    await graph.ainvoke(
        {
            "messages": [
                HumanMessage(
                    content="Meu nome é Marcus, tenho 28 anos e adoro jazz e blues"
                )
            ],
            "userId": test_thread_id,
        },
        config,
    )

    await asyncio.sleep(0.5)

    namespace = ["memories", test_thread_id]
    saved_memories = await memory_service["store"]["search"](namespace, limit=10)

    assert len(saved_memories) > 0, "Deve recuperar informações básicas"

    memories_text = " ".join(
        [m.get("value", {}).get("data", "") for m in saved_memories]
    )
    assert "Marcus" in memories_text, "Deve incluir nome"
    assert "28" in memories_text, "Deve incluir idade"
    assert "jazz" in memories_text.lower() or "blues" in memories_text.lower(), (
        "Deve incluir gêneros"
    )


@pytest.mark.asyncio
async def test_deve_responder_perguntas_simples_sem_extrair_preferencias(graph_setup):
    graph, _ = graph_setup
    test_thread_id = f"test-user-{int(time.time() * 1000)}"
    config = {
        "configurable": {"thread_id": test_thread_id},
        "context": {"userId": test_thread_id},
    }

    response = await graph.ainvoke(
        {
            "messages": [HumanMessage(content="Qual é sua música favorita?")],
            "userId": test_thread_id,
        },
        config,
    )

    assert len(response["messages"]) > 0, "Deve ter resposta"


@pytest.mark.asyncio
async def test_deve_manter_historico_da_conversa(graph_setup):
    graph, _ = graph_setup
    test_thread_id = f"test-user-{int(time.time() * 1000)}"
    config = {
        "configurable": {"thread_id": test_thread_id},
        "context": {"userId": test_thread_id},
    }

    await graph.ainvoke(
        {
            "messages": [HumanMessage(content="Oi, sou Taylor e adoro música pop")],
            "userId": test_thread_id,
        },
        config,
    )

    response2 = await graph.ainvoke(
        {
            "messages": [HumanMessage(content="Pode recomendar algo animado?")],
            "userId": test_thread_id,
        },
        config,
    )

    assert len(response2["messages"]) >= 2, "Deve ter múltiplas mensagens no histórico"

    has_user_message = any(
        msg.type == "human" and "animado" in msg.content
        for msg in response2["messages"]
    )

    assert has_user_message, "Deve manter histórico da conversa"
