from typing import TypedDict

from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langgraph.store.postgres.aio import AsyncPostgresStore
from psycopg_pool import AsyncConnectionPool

from song_highlights.config import config


class MemoryService(TypedDict):
    checkpointer: AsyncPostgresSaver
    store: AsyncPostgresStore


async def create_memory_service() -> MemoryService:
    db_uri = config.memory.db_uri

    pool = AsyncConnectionPool(db_uri, kwargs={"autocommit": True})

    await pool.open()

    store = AsyncPostgresStore(pool)
    checkpointer = AsyncPostgresSaver(pool)

    await store.setup()
    await checkpointer.setup()

    print("✅ Memória configurada: PostgreSQL")

    return {
        "checkpointer": checkpointer,
        "store": store,
    }
