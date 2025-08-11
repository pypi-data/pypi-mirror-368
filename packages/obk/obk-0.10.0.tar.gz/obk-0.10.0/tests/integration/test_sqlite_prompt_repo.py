from pathlib import Path

from obk.domain.prompts.models import Prompt
from obk.infrastructure.db.sqlite import SqlitePromptRepository, _connect


def test_pragmas_and_crud(tmp_path: Path) -> None:
    db = tmp_path / "session.db"
    repo = SqlitePromptRepository(db)
    repo.add(Prompt("1", "2025-08-10", "x"))
    assert [p.id for p in repo.list()] == ["1"]
    with _connect(db) as cx:
        assert cx.execute("PRAGMA foreign_keys").fetchone()[0] == 1
        assert str(cx.execute("PRAGMA journal_mode").fetchone()[0]).upper() == "WAL"
