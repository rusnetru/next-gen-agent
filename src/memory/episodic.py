"""Episodic memory store — SQLite-backed persistence (Phase 0.3)."""

from __future__ import annotations

import json
import sqlite3
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class Episode:
    content: str
    context: dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)


class EpisodicMemory:
    """Persists episodes to a SQLite file. Pass db_path=":memory:" for ephemeral use (tests)."""

    def __init__(self, db_path: str | Path = "memory.db") -> None:
        self._db_path = str(db_path)
        self._conn = sqlite3.connect(self._db_path)
        self._conn.execute(
            """
            CREATE TABLE IF NOT EXISTS episodes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL,
                context TEXT NOT NULL,
                timestamp REAL NOT NULL
            )
            """
        )
        self._conn.commit()

    def store(self, content: str, context: dict[str, Any] | None = None) -> Episode:
        episode = Episode(content=content, context=context or {})
        self._conn.execute(
            "INSERT INTO episodes (content, context, timestamp) VALUES (?, ?, ?)",
            (episode.content, json.dumps(episode.context), episode.timestamp),
        )
        self._conn.commit()
        return episode

    def retrieve(self, query: str, top_k: int = 5) -> list[Episode]:
        matches = [e for e in self.all() if query.lower() in e.content.lower()]
        return matches[-top_k:]

    def all(self) -> list[Episode]:
        rows = self._conn.execute(
            "SELECT content, context, timestamp FROM episodes ORDER BY id"
        ).fetchall()
        return [Episode(content=c, context=json.loads(ctx), timestamp=ts) for c, ctx, ts in rows]

    def count(self) -> int:
        (n,) = self._conn.execute("SELECT COUNT(*) FROM episodes").fetchone()
        return n

    def close(self) -> None:
        self._conn.close()
