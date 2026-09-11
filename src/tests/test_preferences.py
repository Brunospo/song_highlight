import pytest
import pytest_asyncio

from song_highlights.services.preferences_service import PreferencesService


@pytest_asyncio.fixture
async def db_service(tmp_path):
    # Cria um arquivo de banco de dados temporário e isolado para cada teste
    db_file = tmp_path / "test_preferences.db"
    service = PreferencesService(str(db_file))
    await service.setup()
    yield service
    await service.close()


@pytest.mark.asyncio
async def test_store_and_get_summary(db_service):
    user_id = "user_123"
    summary_data = {
        "name": "Maria",
        "age": 30,
        "favorite_genres": ["Rock", "Jazz"],
        "favorite_bands": ["Pink Floyd", "Miles Davis"],
        "keyPreferences": "Gosta de som alto",
        "important_context": "Trabalha ouvindo música",
    }

    await db_service.store_summary(user_id, summary_data)
    result = await db_service.get_summary(user_id)

    assert result is not None
    assert result["name"] == "Maria"
    assert result["age"] == 30
    assert result["favorite_genres"] == ["Rock", "Jazz"]
    assert result["favorite_bands"] == ["Pink Floyd", "Miles Davis"]
    assert result["keyPreferences"] == "Gosta de som alto"


@pytest.mark.asyncio
async def test_merge_preferences(db_service):
    user_id = "user_456"

    initial_data = {
        "name": "João",
        "favorite_genres": ["Pop"],
        "favorite_bands": ["Michael Jackson"],
    }
    await db_service.store_summary(user_id, initial_data)

    new_prefs = {
        "favorite_genres": ["Pop", "Rock"],
        "favorite_bands": ["Queen"],
        "mood": "Animado",
        "listening_context": "Escritório",
    }
    await db_service.merge_preferences(user_id, new_prefs)

    result = await db_service.get_summary(user_id)

    assert result["favorite_genres"] == ["Pop", "Rock"]
    assert result["favorite_bands"] == ["Michael Jackson", "Queen"]
    assert "Mood: Animado" in result["important_context"]
    assert "Context: Escritório" in result["important_context"]


@pytest.mark.asyncio
async def test_get_basic_info(db_service):
    user_id = "user_789"
    await db_service.store_summary(
        user_id, {"name": "Ana", "age": 25, "favorite_genres": ["Eletrônica"]}
    )

    info = await db_service.get_basic_info(user_id)

    assert "Nome: Ana" in info
    assert "Idade: 25" in info
    assert "Gêneros Favoritos: Eletrônica" in info
