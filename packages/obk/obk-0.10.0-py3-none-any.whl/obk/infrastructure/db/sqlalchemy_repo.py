from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import cast

from sqlalchemy import text
from sqlalchemy.engine import Engine

from obk.application.prompts.ports import PromptRepository
from obk.domain.prompts import Prompt


@dataclass(frozen=True)
class SqlAlchemyPromptRepository(PromptRepository):
    """Prompt repository backed by SQLAlchemy Core.

    Assumes STRICT `prompts` table created by `make_engine`.
    """
    engine: Engine

    def add(self, prompt: Prompt) -> None:
        with self.engine.begin() as cx:
            cx.execute(
                text("INSERT INTO prompts(id, date_utc, type) VALUES (:id, :date, :type)"),
                {"id": prompt.id, "date": prompt.date_utc, "type": prompt.type},
            )

    def list(self) -> list[Prompt]:
        with self.engine.begin() as cx:
            result = cx.execute(
                text("SELECT id, date_utc, type FROM prompts ORDER BY date_utc")
            )
            rows = cast(Sequence[Mapping[str, object]], result.mappings().all())
        return [
            Prompt(
                str(row["id"]),
                str(row["date_utc"]),
                str(row["type"]),
            )
            for row in rows
        ]
