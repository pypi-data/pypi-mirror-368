from __future__ import annotations

import sqlite3
from pathlib import Path

from obk.application.prompts.ports import PromptRepository
from obk.domain.prompts import Prompt


def _connect(db: Path) -> sqlite3.Connection:
    con = sqlite3.connect(db)
    con.execute("PRAGMA foreign_keys=ON")
    con.execute("PRAGMA journal_mode=WAL")
    con.execute(
        """
        CREATE TABLE IF NOT EXISTS prompts(
            id TEXT PRIMARY KEY,
            date_utc TEXT NOT NULL,
            type TEXT NOT NULL
        ) STRICT
        """
    )
    return con


class SqlitePromptRepository(PromptRepository):
    def __init__(self, db: Path) -> None:
        self._db = db
        with _connect(self._db):
            pass

    def add(self, p: Prompt) -> None:
        with _connect(self._db) as cx:
            cx.execute(
                "INSERT INTO prompts(id,date_utc,type) VALUES(?,?,?)",
                (p.id, p.date_utc, p.type),
            )

    def list(self) -> list[Prompt]:
        with _connect(self._db) as cx:
            rows = cx.execute(
                "SELECT id,date_utc,type FROM prompts ORDER BY date_utc"
            ).fetchall()
        return [Prompt(*r) for r in rows]
