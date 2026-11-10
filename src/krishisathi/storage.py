"""SQLite persistence layer for farmer profiles and recent call summaries."""

from __future__ import annotations

import logging
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator

from krishisathi.config import settings
from krishisathi.languages import normalize_language

logger = logging.getLogger("krishisathi.storage")

MAX_SUMMARIES_PER_FARMER = 5


class FarmerRepository:
    """Manages persistent farmer profiles and rolling conversation summaries."""

    def __init__(self, db_path: str | Path | None = None) -> None:
        self.db_path = Path(db_path or settings.db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_schema()

    @contextmanager
    def _connect(self) -> Iterator[sqlite3.Connection]:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()

    def _init_schema(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS farmers (
                    phone TEXT PRIMARY KEY,
                    name TEXT,
                    place TEXT,
                    state TEXT,
                    crops TEXT,
                    preferred_language TEXT DEFAULT 'hindi',
                    registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    phone TEXT NOT NULL,
                    summary TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (phone) REFERENCES farmers (phone)
                )
                """
            )
        logger.debug("SQLite schema ready at %s", self.db_path)

    def get_farmer(self, phone: str) -> dict[str, Any] | None:
        """Fetch a farmer profile along with their 5 most recent call summaries."""
        with self._connect() as conn:
            farmer = conn.execute(
                "SELECT phone, name, place, state, crops, preferred_language FROM farmers WHERE phone = ?",
                (phone,),
            ).fetchone()
            if farmer is None:
                return None

            rows = conn.execute(
                """
                SELECT summary FROM conversations
                WHERE phone = ?
                ORDER BY timestamp DESC, id DESC
                LIMIT ?
                """,
                (phone, MAX_SUMMARIES_PER_FARMER),
            ).fetchall()

        return {
            "phone": farmer["phone"],
            "name": farmer["name"],
            "place": farmer["place"],
            "state": farmer["state"],
            "crops": farmer["crops"],
            "preferred_language": farmer["preferred_language"] or "hindi",
            "history": [row["summary"] for row in rows],
        }

    def register_farmer(
        self,
        phone: str,
        name: str,
        place: str,
        state: str,
        crops: str,
        language: str = "hindi",
    ) -> None:
        """Create or update a farmer profile while preserving original registration time."""
        normalized_lang = normalize_language(language)
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO farmers (phone, name, place, state, crops, preferred_language)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(phone) DO UPDATE SET
                    name = excluded.name,
                    place = excluded.place,
                    state = excluded.state,
                    crops = excluded.crops,
                    preferred_language = excluded.preferred_language
                """,
                (phone, name, place, state, crops, normalized_lang),
            )
        logger.info("Saved profile for %s (%s) in %s, %s", name, phone, place, state)

    def update_language(self, phone: str, language: str) -> None:
        """Update only the preferred language for an existing farmer."""
        normalized_lang = normalize_language(language)
        with self._connect() as conn:
            conn.execute(
                "UPDATE farmers SET preferred_language = ? WHERE phone = ?",
                (normalized_lang, phone),
            )
        logger.info("Updated preferred language for %s to %s", phone, normalized_lang)

    def update_farmer_details(
        self,
        phone: str,
        name: str | None = None,
        place: str | None = None,
        state: str | None = None,
        crops: str | None = None,
    ) -> bool:
        """Update specific profile fields for a farmer. Returns True if applied."""
        updates: list[str] = []
        params: list[Any] = []

        for field_name, value in (
            ("name", name),
            ("place", place),
            ("state", state),
            ("crops", crops),
        ):
            if value is not None:
                updates.append(f"{field_name} = ?")
                params.append(value)

        if not updates:
            return False

        params.append(phone)
        with self._connect() as conn:
            cursor = conn.execute(
                f"UPDATE farmers SET {', '.join(updates)} WHERE phone = ?",
                tuple(params),
            )
        updated = cursor.rowcount > 0
        logger.info("Updated profile for %s (changed=%s)", phone, updated)
        return updated

    def add_summary(self, phone: str, summary: str) -> None:
        """Append a call summary and prune older entries beyond the retention limit."""
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO conversations (phone, summary) VALUES (?, ?)",
                (phone, summary),
            )
            conn.execute(
                """
                DELETE FROM conversations
                WHERE phone = ? AND id NOT IN (
                    SELECT id FROM conversations
                    WHERE phone = ?
                    ORDER BY timestamp DESC, id DESC
                    LIMIT ?
                )
                """,
                (phone, phone, MAX_SUMMARIES_PER_FARMER),
            )
        logger.info("Recorded call summary for %s", phone)


repository = FarmerRepository()

