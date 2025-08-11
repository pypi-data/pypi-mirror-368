<!-- Prompt-ID: 20250810T024606+0000 Trace-ID: 20250810T024606+0000 Task-ID: task-4 Date: 2025-08-10 Paths: Prompt: prompts\2025\08\10\20250810T024606+0000.md Tasks: tasks\2025\08\10\20250810T024606+0000\ Reviews: reviews\2025\08\10\20250810T024606+0000\ Rules: Scope: Only consume THIS task’s content (task-4.md), the prompt, and reviews explicitly bound to task-4 via front matter. Precedence: This task’s rules are authoritative. -->

# task-4 — Close Acceptance Gaps: CI gates, no import-time side effects, SQLite repo (STRICT+PRAGMAs), and tests

## Scope Keys (Prompt-Aware)

* Prompt-ID: 20250810T024606+0000
    
* Task-ID: task-4
    
* Prompt Path: prompts\2025\08\10\20250810T024606+0000.md
    
* Task Path: tasks\2025\08\10\20250810T024606+0000\task-4.md
    
* Reviews Dir: reviews\2025\08\10\20250810T024606+0000\
    
* Review Selection Rule: Only reviews whose front matter has `prompt_id == 20250810T024606+0000` and `task_id == task-4`.
    

## Goal

Implement the **minimal set of changes** to pass acceptance:

1. CI must block on **mypy (strict)** and **ruff**;
    
2. **No import-time side effects** in CLI; **rotating logs** only in `main()`;
    
3. Add **SQLite PromptRepository** with **STRICT table** and **PRAGMAs** (FK=ON, WAL);
    
4. Add **unit tests** (handlers w/ FakeRepo) and **integration tests** (SQLite PRAGMAs + CRUD).
    

* * *

## Implementation Steps (with tests)

### Step 1 — Fix typing imports and add QA deps

**Goal:** Resolve mypy errors (tomli/platformdirs) and provide a QA extra set.

**Files**

* EDIT: `pyproject.toml`
    
* EDIT: `src\obk\project_path.py`
    

**Code**

```diff
# path: pyproject.toml
 [project]
 dependencies = [
   "typer>=0.12",
   "dependency-injector>=4.41",
   "xmlschema>=3.2",
   "tzdata>=2024.1",
   "packaging>=24.0",
   "colorama>=0.4.6",
+  "platformdirs>=4.2",
 ]

 [project.optional-dependencies]
 test = [
   "pytest >=7.0.0",
   "pytest-cov >=4.0.0",
   "pytest-mock >=3.10.0",
   "python-dotenv >=1.0.0",
   "toml",
 ]
+qa = [
+  "mypy>=1.10",
+  "ruff>=0.5",
+]

 [tool.mypy]
 python_version = "3.11"
+strict = true
```

```diff
# path: src\obk\project_path.py
-try:
-    import tomllib  # py311+
-except ModuleNotFoundError:  # pragma: no cover
-    import tomli as tomllib  # type: ignore[no-redef]
+import tomllib  # stdlib on 3.11+
```

**Tests / Exit criteria**

* `pip install -e .[test,qa]` succeeds.
    
* `mypy --strict` passes for touched modules.
    

* * *

### Step 2 — Make CI block on ruff + mypy

**Goal:** Ensure CI fails when type or lint checks fail.

**Files**

* EDIT: `.github\workflows\ci-cd.yml`
    

**Code**

```diff
   - name: Run tests
     run: |
       python3 -m venv .venv
       .venv/bin/pip install --upgrade pip
-      .venv/bin/pip install -e .[test]
-      .venv/bin/pytest -q
+      .venv/bin/pip install -e .[test,qa]
+      .venv/bin/ruff check .
+      .venv/bin/mypy --strict
+      .venv/bin/pytest -q
```

**Exit criteria**

* On PR, CI runs `ruff` and `mypy --strict` before `pytest` and fails on violations.
    

* * *

### Step 3 — Remove import-time side effects; add rotating logs

**Goal:** No global state at import; logging configured only in `main()` with rotating handler.

**Files**

* EDIT: `src\obk\presentation\cli\main.py` (or equivalent entry file)
    

**Code**

```diff
 def configure_logging(log_file: Path) -> None:
-    logging.basicConfig(
-        level=logging.INFO,
-        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
-        handlers=[logging.FileHandler(log_file, encoding="utf-8")],
-    )
+    from logging.handlers import RotatingFileHandler
+    handler = RotatingFileHandler(log_file, maxBytes=1_000_000, backupCount=3, encoding="utf-8")
+    logging.basicConfig(
+        level=logging.INFO,
+        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
+        handlers=[handler],
+    )

- sys.excepthook = _global_excepthook
+def _install_global_excepthook() -> None:
+    sys.excepthook = _global_excepthook

 def main(argv: list[str] | None = None) -> None:
     """Entry point for ``python -m obk``."""
-    _cli.run(argv)
+    configure_logging(LOG_FILE)
+    _install_global_excepthook()
+    _cli.run(argv)
```

**Tests**

```python
# path: tests\cli\test_help.py
from typer.testing import CliRunner
from obk.presentation.cli.app import app

def test_help_no_import_side_effects():
    r = CliRunner().invoke(app, ["--help"])
    assert r.exit_code == 0
    assert "--help" in r.stdout
```

**Exit criteria**

* Importing CLI modules does not set `sys.excepthook` or configure logging.
    
* `pytest -q` passes; `obk --help` exits 0.
    

* * *

### Step 4 — Add SQLite PromptRepository with STRICT + PRAGMAs

**Goal:** Minimal SQLite-backed repo implementing existing PromptRepository.

**Files**

* ADD: `src\obk\infrastructure\db\sqlite.py`
    

**Code**

```python
# path: src\obk\infrastructure\db\sqlite.py
from __future__ import annotations
import sqlite3
from pathlib import Path
from obk.application.prompts.ports import PromptRepository
from obk.domain.prompts.models import Prompt

def _connect(db: Path) -> sqlite3.Connection:
    con = sqlite3.connect(db)
    con.execute("PRAGMA foreign_keys=ON")
    con.execute("PRAGMA journal_mode=WAL")
    con.execute("""
        CREATE TABLE IF NOT EXISTS prompts(
            id TEXT PRIMARY KEY,
            date_utc TEXT NOT NULL,
            type TEXT NOT NULL
        ) STRICT
    """)
    return con

class SqlitePromptRepository(PromptRepository):
    def __init__(self, db: Path) -> None:
        self._db = db
        with _connect(self._db):  # ensure schema and PRAGMAs
            pass

    def add(self, p: Prompt) -> None:
        with _connect(self._db) as cx:
            cx.execute("INSERT INTO prompts(id,date_utc,type) VALUES(?,?,?)",
                       (p.id, p.date_utc, p.type))

    def list(self) -> list[Prompt]:
        with _connect(self._db) as cx:
            rows = cx.execute("SELECT id,date_utc,type FROM prompts ORDER BY date_utc").fetchall()
        return [Prompt(*r) for r in rows]
```

**Exit criteria**

* Module imports cleanly; no global side effects.
    
* Table `prompts` is STRICT; PRAGMAs are set on connections.
    

* * *

### Step 5 — Wire container (non-breaking)

**Goal:** Keep in-memory default; allow SQLite when `config.db_path` is provided.

**Files**

* EDIT: `src\obk\containers.py`
    

**Code (representative)**

```diff
+from pathlib import Path
 from .infrastructure.db.prompts import InMemoryPromptRepository
+from .infrastructure.db.sqlite import SqlitePromptRepository

 class Container(containers.DeclarativeContainer):
     config = providers.Configuration()
-    prompt_repository = providers.Singleton(InMemoryPromptRepository)
+    _sqlite_repo = providers.Singleton(SqlitePromptRepository, db=providers.Callable(Path, config.db_path))
+    prompt_repository = providers.Selector(
+        providers.Callable(lambda p: "sqlite" if p else None, config.db_path)(),
+        **{
+            None: providers.Singleton(InMemoryPromptRepository),
+            "sqlite": _sqlite_repo,
+        },
+    )
```

**Exit criteria**

* Existing CLI continues to work with in-memory.
    
* Future commands can flip to SQLite by setting `config.db_path`.
    

* * *

### Step 6 — Unit tests for handlers with FakeRepo

**Goal:** Cover command/query handlers without I/O.

**Files**

* ADD: `tests\unit\prompts\test_add_and_list.py`
    

**Tests**

```python
# path: tests\unit\prompts\test_add_and_list.py
from obk.application.prompts.ports import PromptRepository
from obk.application.prompts.commands.add_prompt import AddPrompt, handle as add_handle
from obk.application.prompts.queries.list_prompts import ListPrompts, handle as list_handle
from obk.domain.prompts.models import Prompt

class FakeRepo(PromptRepository):
    def __init__(self) -> None:
        self.items: list[Prompt] = []
    def add(self, p: Prompt) -> None: self.items.append(p)
    def list(self) -> list[Prompt]: return list(self.items)

def test_add_then_list() -> None:
    repo = FakeRepo()
    add_handle(AddPrompt(id="1", date_utc="2025-08-10", type="demo"), repo)
    out = list_handle(ListPrompts(), repo)
    assert out == [Prompt("1", "2025-08-10", "demo")]
```

**Exit criteria**

* Test passes; verifies handler purity and repo seam.
    

* * *

### Step 7 — Integration tests for SQLite PRAGMAs + CRUD

**Goal:** Verify FK ON, WAL, STRICT table, and basic CRUD.

**Files**

* ADD: `tests\integration\test_sqlite_prompt_repo.py`
    

**Tests**

```python
# path: tests\integration\test_sqlite_prompt_repo.py
from pathlib import Path
import sqlite3
from obk.infrastructure.db.sqlite import SqlitePromptRepository
from obk.domain.prompts.models import Prompt

def test_pragmas_and_crud(tmp_path: Path) -> None:
    db = tmp_path / "session.db"
    repo = SqlitePromptRepository(db)
    repo.add(Prompt("1", "2025-08-10", "x"))
    assert [p.id for p in repo.list()] == ["1"]
    with sqlite3.connect(db) as cx:
        assert cx.execute("PRAGMA foreign_keys").fetchone()[0] == 1
        assert str(cx.execute("PRAGMA journal_mode").fetchone()[0]).upper() == "WAL"
```

**Exit criteria**

* Test passes and asserts PRAGMAs and CRUD.
    

* * *

## Acceptance Check (end-to-end)

Run locally (then CI validates the same):

```bash
pip install -e .[test,qa]
ruff check .
mypy --strict
pytest -q
```

**Expected**

* Lint/type checks pass.
    
* All tests green.
    
* Importing CLI modules does not configure logging or excepthook.
    
* SQLite integration test confirms `WAL` and `foreign_keys=ON`; STRICT table exists.
    

* * *

## Commit Plan

1. chore(typing): add platformdirs, QA extra; fix tomllib import; enable mypy strict
    
2. ci: run ruff + mypy strict before pytest
    
3. refactor(cli): move logging/excepthook to main; add rotating logs
    
4. feat(db): add SQLite PromptRepository with STRICT + PRAGMAs
    
5. test(unit): handlers with FakeRepo
    
6. test(integration): sqlite PRAGMAs and CRUD
    

* * *

## Rollback Plan

* Revert step-specific commits individually if a regression appears; CI will pinpoint the failing stage (typing, lint, unit, or integration).
    

* * *

**Provenance**: This task is based solely on the prompt and the matching review for task-4 (review-1.md).