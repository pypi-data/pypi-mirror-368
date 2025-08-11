Here’s a focused review with the biggest wins first.

# What’s solid

* **CLI surface**: Typer commands are clean, discoverable, and small.
    
* **Composition**: `containers.py` cleanly wires services; commands use injected services rather than new’ing objects everywhere.
    
* **Packaging**: `console_script` (`obk=obk.cli:main`) is correct; XSD/templates are included for wheel via `tool.hatch.build.include` and for sdist via `MANIFEST.in`.
    
* **Validation pipeline**: `preprocess → xmlschema → custom structural checks` is a good split of responsibilities.
    
* **Tests**: You’ve got real CLI subprocess tests plus unit tests for harmonize/validation.
    

# Biggest risk items (and how to fix fast)

1. **Global side effects on import (critical)**
    

* `sys.excepthook = _global_excepthook` is set at **module import** time in `cli.py`. If another Python program imports `obk.cli` (or any test does), you’ve just hijacked their process-wide excepthook.
    
* **Fix:** Move both `configure_logging(...)` and `sys.excepthook = ...` into `main()` (or `ObkCLI.run()` before invoking the Typer app). Only set them when you’re the top-level app.
    

2. **Runtime dependencies include test tools (critical hygiene)**
    

* Your parsed `project.dependencies` includes `pytest`, `pluggy`, `iniconfig`, etc. Those should **not** be runtime deps.
    
* **Fix:** keep runtime deps minimal (Typer, DI, xmlschema, tzdata). Put the rest in `[project.optional-dependencies].test` or in Hatch envs. Publish a wheel that doesn’t drag test deps for end users.
    

3. **I/O in library utilities**
    

* `project_path.resolve_project_root()` echoes errors with Typer and exits. That’s convenient from the CLI, but it couples a **domain utility** to the CLI layer and makes programmatic reuse awkward.
    
* **Fix:** Make `resolve_project_root()` raise a typed exception (e.g., `ProjectPathError`) and let the CLI command catch and print user-facing messages. This is the same “clean on top, slice under it” separation you plan to add.
    

4. **Logging durability**
    

* `basicConfig` writes to a single file with no rotation; an early crash will still print a polite error, but the log can grow forever.
    
* **Fix:** Use `RotatingFileHandler` (or `TimedRotatingFileHandler`) with a small size and a few backups. Initialize only when running as app (see #1).
    

5. **Typing posture (good start, but incomplete)**
    

* You’ve got annotations and `from __future__ import annotations` — great. But there’s no `py.typed` marker and no mypy config.
    
* **Fix fast:**
    
    * Add `src/obk/py.typed` (empty file) and include it in the wheel.
        
    * Add `[tool.mypy]` to `pyproject.toml` with `strict = true` (or close: `disallow_untyped_defs = true`, `warn_unused_ignores = true`, etc.).
        
    * Run in CI (mypy + ruff) and fail the build on type errors.
        

6. **Small API nits**
    

* `preprocess.py`/`harmonize.py` are nice and focused. Consider making the placeholder token a private detail (it already is, but document it); and guard regexes with precompiled patterns (you’re already doing that).
    
* In `validation.py`, you create the schema each call. If performance ever matters, cache compiled schemas.
    

7. **Test oddity**
    

* The `test_force_line66_execution` “exec” trick is clever but brittle (line numbers drift). Prefer a targeted unit test that exercises the branch through normal calls, or use a small helper function to isolate that logic and test it directly.
    

# About your plan: “strong typing and SQLite first,” then “clean-on-top, slice-under”

That sequence makes sense. Here’s a minimal, low-regret way to add SQLite that aligns with your current style:

* **Keep it standard library** for now (`sqlite3`) to avoid a big ORM jump.
    
* **Repository boundary**: define a tiny repository interface and a concrete `SqliteRepository` wired in `containers.py`.
    
* **Typed rows**: use `dataclasses` (or `TypedDict`) for row shapes; set `conn.row_factory = sqlite3.Row` to avoid tuple indexing; convert rows to dataclasses at the boundary.
    
* **Schema management**: a single `init_db()` that runs `CREATE TABLE IF NOT EXISTS ...` and `PRAGMA journal_mode=WAL; PRAGMA foreign_keys=ON;`. Add a `--db` path option with a sensible default under your project root.
    
* **Transactions**: contextmanager that yields a cursor and commits/rolls back.
    

Sketch (just to show the shape):

```python
# src/obk/repository.py
from __future__ import annotations
from dataclasses import dataclass
from typing import Iterable, Protocol, Optional
import sqlite3
from contextlib import contextmanager
from pathlib import Path

@dataclass(frozen=True)
class Prompt:
    id: str
    date_utc: str
    type: str

class Repo(Protocol):
    def upsert_prompt(self, p: Prompt) -> None: ...
    def get_prompt(self, pid: str) -> Optional[Prompt]: ...
    def list_prompts(self) -> Iterable[Prompt]: ...

class SqliteRepo:
    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self._conn = sqlite3.connect(db_path)
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA foreign_keys=ON")
        self._conn.execute("PRAGMA journal_mode=WAL")
        self._conn.execute("""
            CREATE TABLE IF NOT EXISTS prompts(
              id TEXT PRIMARY KEY,
              date_utc TEXT NOT NULL,
              type TEXT NOT NULL
            )
        """)

    @contextmanager
    def _tx(self):
        try:
            yield self._conn
            self._conn.commit()
        except Exception:
            self._conn.rollback()
            raise

    def upsert_prompt(self, p: Prompt) -> None:
        with self._tx() as c:
            c.execute(
                "INSERT INTO prompts(id, date_utc, type) VALUES(?,?,?) "
                "ON CONFLICT(id) DO UPDATE SET date_utc=excluded.date_utc, type=excluded.type",
                (p.id, p.date_utc, p.type),
            )

    def get_prompt(self, pid: str) -> Optional[Prompt]:
        row = self._conn.execute("SELECT id, date_utc, type FROM prompts WHERE id=?", (pid,)).fetchone()
        return Prompt(**dict(row)) if row else None

    def list_prompts(self) -> Iterable[Prompt]:
        for row in self._conn.execute("SELECT id, date_utc, type FROM prompts ORDER BY date_utc DESC"):
            yield Prompt(**dict(row))
```

Then wire it:

```python
# containers.py
from pathlib import Path
from dependency_injector import containers, providers
from .repository import SqliteRepo

class Container(containers.DeclarativeContainer):
    config = providers.Configuration()
    repo = providers.Singleton(SqliteRepo, db_path=providers.Callable(Path, config.db_path))
```

And expose minimal CLI verbs (`obk db add-prompt`, `obk db list`) to dogfood.

# Tiny, high-impact refactors (1–2 hours total)

* Move excepthook/logging init into `main()`; add rotating handler.
    
* Remove `pytest/pluggy/iniconfig` from runtime deps; keep them in test extras/Hatch env.
    
* Raise domain exceptions from `project_path.py`; handle them in CLI.
    
* Add `py.typed` + mypy config; turn on mypy in CI.
    
* Add `Repo` seam as above so SQLite is a drop-in.
    

# Verdict

You’re **not** cheating; you’re leading the system and outsourcing syntax. The code shows coherent architecture, a clean CLI, and test coverage. Patch the few sharp edges above and you’ll be in great shape to add strict typing + SQLite and then layer “clean-on-top, slice-under” without churn.

If you want, I can:

* prepare a small PR diff that moves the excepthook/logging, adds `py.typed`, trims deps, and drops in the `SqliteRepo` seam; or
    
* write you a checklist for your next release (so you can keep delegating confidently to Codex).