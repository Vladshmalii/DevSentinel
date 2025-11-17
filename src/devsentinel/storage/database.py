"""SQLite persistence for notes and sessions."""
from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable


@dataclass(slots=True)
class StorageConfig:
    path: Path = Path("devsentinel.db")


class Storage:
    def __init__(self, config: StorageConfig):
        self.config = config
        self._conn = sqlite3.connect(self.config.path)
        self._conn.row_factory = sqlite3.Row
        self._ensure_schema()

    def _ensure_schema(self) -> None:
        cur = self._conn.cursor()
        cur.executescript(
            """
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL,
                created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                kind TEXT NOT NULL,
                started_at TEXT NOT NULL,
                duration_minutes INTEGER NOT NULL
            );
            """
        )
        self._conn.commit()

    def save_note(self, content: str) -> None:
        cur = self._conn.cursor()
        cur.execute(
            "INSERT INTO notes (content, created_at) VALUES (?, ?)",
            (content, datetime.utcnow().isoformat()),
        )
        self._conn.commit()

    def save_session(self, kind: str, duration_minutes: int) -> None:
        cur = self._conn.cursor()
        cur.execute(
            "INSERT INTO sessions (kind, started_at, duration_minutes) VALUES (?, ?, ?)",
            (kind, datetime.utcnow().isoformat(), duration_minutes),
        )
        self._conn.commit()

    def list_notes(self) -> Iterable[str]:
        cur = self._conn.cursor()
        cur.execute("SELECT content FROM notes ORDER BY id DESC LIMIT 20")
        for row in cur.fetchall():
            yield row["content"]
