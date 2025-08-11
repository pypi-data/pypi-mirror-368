from __future__ import annotations

import sqlite3
from pathlib import Path

from sqlalchemy import create_engine, event, text
from sqlalchemy.engine import Engine


def make_engine(db: Path) -> Engine:
    e = create_engine(f"sqlite+pysqlite:///{db}", future=True)

    def _pragma(dbapi_con: sqlite3.Connection, _connection_record: object) -> None:
        cursor = dbapi_con.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.close()

    event.listen(e, "connect", _pragma)

    with e.begin() as cx:
        cx.execute(
            text(
                """
                CREATE TABLE IF NOT EXISTS prompts(
                  id TEXT PRIMARY KEY,
                  date_utc TEXT NOT NULL,
                  type TEXT NOT NULL
                ) STRICT
                """
            )
        )
    return e
