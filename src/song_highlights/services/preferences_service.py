import json
import sqlite3
from typing import Any


class PreferencesService:
    def __init__(self, db_path: str):
        self.db_path = db_path.replace("file:", "")
        self.is_setup = False

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    async def setup(self) -> None:
        if self.is_setup:
            return

        with self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS user_preferences (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT UNIQUE NOT NULL,
                    name TEXT,
                    age INTEGER,
                    favorite_genres TEXT,
                    favorite_bands TEXT,
                    key_preferences TEXT,
                    important_context TEXT,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()

        self.is_setup = True

    async def merge_preferences(self, user_id: str, prefs: dict[str, Any]) -> None:
        await self.setup()

        existing = await self.get_summary(user_id)

        existing_genres = existing.get("favorite_genres", []) if existing else []
        new_genres = prefs.get("favorite_genres", [])
        merged_genres = (
            list(dict.fromkeys(existing_genres + new_genres))
            if new_genres
            else existing_genres
        )

        existing_bands = existing.get("favorite_bands", []) if existing else []
        new_bands = prefs.get("favorite_bands", [])
        merged_bands = (
            list(dict.fromkeys(existing_bands + new_bands))
            if new_bands
            else existing_bands
        )

        context_parts = [
            existing.get("important_context") if existing else None,
            f"Mood: {prefs.get('mood')}" if prefs.get("mood") else None,
            f"Context: {prefs.get('listening_context')}"
            if prefs.get("listening_context")
            else None,
            prefs.get("additional_info"),
        ]
        context_parts = [p for p in context_parts if p]

        name = prefs.get("name") or (existing.get("name") if existing else None)
        age = prefs.get("age") or (existing.get("age") if existing else None)
        key_preferences = existing.get("keyPreferences") if existing else None
        important_context = ". ".join(context_parts) if context_parts else None

        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT INTO user_preferences (
                    user_id, name, age, favorite_genres, favorite_bands, key_preferences, important_context, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(user_id) DO UPDATE SET
                    name = COALESCE(excluded.name, name),
                    age = COALESCE(excluded.age, age),
                    favorite_genres = COALESCE(excluded.favorite_genres, favorite_genres),
                    favorite_bands = COALESCE(excluded.favorite_bands, favorite_bands),
                    key_preferences = COALESCE(excluded.key_preferences, key_preferences),
                    important_context = COALESCE(excluded.important_context, important_context),
                    updated_at = CURRENT_TIMESTAMP
            """,
                (
                    user_id,
                    name,
                    age,
                    json.dumps(merged_genres) if merged_genres else None,
                    json.dumps(merged_bands) if merged_bands else None,
                    key_preferences,
                    important_context,
                ),
            )
            conn.commit()

    async def store_summary(self, user_id: str, summary: dict[str, Any]) -> None:
        await self.setup()

        favorite_genres = summary.get("favorite_genres")
        favorite_bands = summary.get("favorite_bands")

        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT INTO user_preferences (
                    user_id, name, age, favorite_genres, favorite_bands, key_preferences, important_context, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(user_id) DO UPDATE SET
                    name = excluded.name,
                    age = excluded.age,
                    favorite_genres = excluded.favorite_genres,
                    favorite_bands = excluded.favorite_bands,
                    key_preferences = excluded.key_preferences,
                    important_context = excluded.important_context,
                    updated_at = CURRENT_TIMESTAMP
            """,
                (
                    user_id,
                    summary.get("name"),
                    summary.get("age"),
                    json.dumps(favorite_genres) if favorite_genres else None,
                    json.dumps(favorite_bands) if favorite_bands else None,
                    summary.get("keyPreferences"),
                    summary.get("important_context"),
                ),
            )
            conn.commit()

    async def get_summary(self, user_id: str) -> dict[str, Any] | None:
        await self.setup()

        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM user_preferences WHERE user_id = ?", (user_id,)
            )
            row = cursor.fetchone()

        if not row:
            return None

        return {
            "name": row["name"],
            "age": row["age"],
            "favorite_genres": json.loads(row["favorite_genres"])
            if row["favorite_genres"]
            else None,
            "favorite_bands": json.loads(row["favorite_bands"])
            if row["favorite_bands"]
            else None,
            "keyPreferences": row["key_preferences"],
            "important_context": row["important_context"],
        }

    async def get_basic_info(self, user_id: str) -> str | None:
        summary = await self.get_summary(user_id)
        if not summary:
            return None

        parts = []

        if summary.get("name"):
            parts.append(f"Nome: {summary['name']}")
        if summary.get("age"):
            parts.append(f"Idade: {summary['age']}")
        if summary.get("favorite_genres"):
            parts.append(f"Gêneros Favoritos: {', '.join(summary['favorite_genres'])}")
        if summary.get("favorite_bands"):
            parts.append(
                f"Artistas/Bandas Favoritas: {', '.join(summary['favorite_bands'])}"
            )
        if summary.get("keyPreferences"):
            parts.append(f"\nPreferências: {summary['keyPreferences']}")

        return "\n".join(parts) if parts else None

    async def close(self) -> None:
        pass
