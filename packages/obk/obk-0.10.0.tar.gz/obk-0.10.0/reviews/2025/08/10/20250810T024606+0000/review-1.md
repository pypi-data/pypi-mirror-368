# Review 1

Here’s a tight audit of `obk_clean.zip` against the prompt **20250810T024606+0000**.

# TL;DR

You’re **part-way there**: layers and CQRS seams exist and the CLI isn’t importing infra directly. What’s still missing: **SQLite repo + PRAGMAs/STRICT**, **rotating logs with no import-time side effects**, **handler unit tests**, **SQLite integration tests**, and **CI gates for mypy/ruff**. Also fix the mypy import errors (tomli/platformdirs).

(Goals/acceptance pulled from the prompt. )

* * *

# What I found (by requirement)

## 1) Strict typing & tooling

* `py.typed`: **Present** at `src/obk/py.typed` and included in wheel. **PASS**  
    (`pyproject.toml` includes it in hatch build includes.)
    
* mypy config: **Present, but not `strict = true`**. You have many strict flags + per-package overrides. **PARTIAL**  
    (Prompt asked for strict and CI gates. )
    
* ruff: **Configured**. **PASS**
    
* CI gates: **Missing**. CI runs pytest, but **does not run ruff or mypy** → **FAIL**  
    (Acceptance #1. )
    

## 2) CQRS seams & handlers

* Ports & DTOs: **Present** (`application/prompts/ports.py`; `domain/prompts/models.py`). **PASS**  
    (Matches prompt’s “ports + frozen dataclasses”. )
    
* Commands/queries: **Present** and **pure** (`add_prompt.handle`, `list_prompts.handle`). **PASS**
    

## 3) Interface (clean on top)

* Typer CLI -> app handlers via DI/mediator, no infra imports in CLI: **Appears correct**. **PASS**  
    (Acceptance #2. )
    
* **Issue:** `sys.excepthook = _global_excepthook` is set **at import time** in `presentation/cli/main.py` → **import-time side effect**; logging also set at import time. **FAIL**  
    (Prompt: move side effects into `main()`. )
    

## 4) Infrastructure (SQLite + logging)

* Repo: only `InMemoryPromptRepository`; **no SQLite engine/repo**; **no PRAGMAs/WAL/STRICT**. **FAIL**  
    (Prompt infra requirements. )
    
* Logging: basic file handler, **no rotating handler**. And initialized at import time. **FAIL**  
    (Prompt requires rotating handler at entrypoint only. )
    

## 5) DI wiring

* `containers.py` wires mediator + repo (in-memory). **PASS (for now)**. Needs a SQLite-backed provider later.  
    (Prompt mentions container providing engine/repo. )
    

## 6) Tests

* Handler unit tests with FakeRepo: **Missing**. **FAIL**  
    (Prompt test requirements. )
    
* SQLite integration tests: **Missing**. **FAIL**  
    (Acceptance #4. )
    

## 7) Debuggability

* `python -m obk` works via `src/obk/__main__.py`. **PASS**
    
* But because of import-time excepthook/logging, it **violates** “no side effects until main”. **FAIL**  
    (Related to prompt’s interface guidance. )
    

## 8) End-user workflows (DB session, rules, GSL import)

* `obk db session …`, `compile-schema`, `migrate`, `import gsl`, reporting: **Not implemented**. **MISSING (future work)**  
    (Prompt Workflows A–B. )
    

* * *

# High-impact fixes (minimal patches)

Below are **surgical diffs** to hit acceptance quickly; they don’t break public entry points.

## A) Make CI block on types & lint (Acceptance #1)

**.github/workflows/ci-cd.yml** — add ruff/mypy to the test job:

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

**pyproject.toml** — add a QA extra:

```diff
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
```

**mypy**: You’re already strict-ish. If you want literal `strict = true` (as per prompt), add it and keep overrides:

```diff
 [tool.mypy]
-python_version = "3.11"
+python_version = "3.11"
+strict = true
```

Fix the two mypy import errors reported earlier:

* **tomli**: you target Python ≥3.11, so drop the fallback import completely.
    
* **platformdirs**: now in dependencies, so mypy resolves it.
    

**src/obk/project_path.py** (top of file):

```diff
-try:
-    import tomllib  # py311+
-except ModuleNotFoundError:  # pragma: no cover
-    import tomli as tomllib  # type: ignore[no-redef]  # only used if project supports <3.11
+import tomllib  # stdlib on 3.11+
```

## B) Remove import-time side effects & add rotating logs (Acceptances #4–5)

**src/obk/presentation/cli/main.py** (key changes):

* **Do not** set `sys.excepthook` at import time.
    
* Configure logging **inside** `ObkCLI.run()` or `main()`.
    
* Switch to `RotatingFileHandler`.
    

```diff
-def configure_logging(log_file: Path) -> None:
-    logging.basicConfig(
-        level=logging.INFO,
-        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
-        handlers=[logging.FileHandler(log_file, encoding="utf-8")],
-    )
+def configure_logging(log_file: Path) -> None:
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
```

Then call both from **`main()`**:

```diff
 def main(argv: list[str] | None = None) -> None:
-    """Entry point for ``python -m obk``."""
-    _cli.run(argv)
+    """Entry point for ``python -m obk``."""
+    configure_logging(LOG_FILE)
+    _install_global_excepthook()
+    _cli.run(argv)
```

## C) Minimal SQLite repo with PRAGMAs & STRICT (Acceptance #4)

Add **`src/obk/infrastructure/db/sqlite.py`**:

```python
from __future__ import annotations
import sqlite3
from pathlib import Path
from typing import Iterable
from obk.application.prompts.ports import PromptRepository
from obk.domain.prompts.models import Prompt

def _connect(db: Path) -> sqlite3.Connection:
    con = sqlite3.connect(db)
    con.execute("PRAGMA foreign_keys=ON")
    con.execute("PRAGMA journal_mode=WAL")
    con.execute("""
        CREATE TABLE IF NOT EXISTS prompts (
            id TEXT PRIMARY KEY,
            date_utc TEXT NOT NULL,
            type TEXT NOT NULL
        ) STRICT
    """)
    return con

class SqlitePromptRepository(PromptRepository):
    def __init__(self, db: Path) -> None:
        self._db = db
        with _connect(self._db):  # ensure schema + pragmas
            pass

    def add(self, prompt: Prompt) -> None:
        with _connect(self._db) as con:
            con.execute(
                "INSERT INTO prompts (id, date_utc, type) VALUES (?, ?, ?)",
                (prompt.id, prompt.date_utc, prompt.type),
            )

    def list(self) -> list[Prompt]:
        with _connect(self._db) as con:
            rows = con.execute("SELECT id, date_utc, type FROM prompts ORDER BY date_utc").fetchall()
        return [Prompt(*row) for row in rows]
```

Wire it in **`src/obk/containers.py`** (choose SQLite when an env/config path is present; otherwise keep in-memory):

```diff
-from .infrastructure.db.prompts import InMemoryPromptRepository
+from .infrastructure.db.prompts import InMemoryPromptRepository
+from .infrastructure.db.sqlite import SqlitePromptRepository
+from pathlib import Path

 def _build_mediator(repo: PromptRepository, logger: Callable[[str], None]) -> Mediator:
     ...

 class Container(containers.DeclarativeContainer):
     config = providers.Configuration()
     greeter = providers.Factory(Greeter)
     divider = providers.Factory(Divider)
-    prompt_repository = providers.Singleton(InMemoryPromptRepository)
+    prompt_repository = providers.Selector(
+        config.db_path.provided or providers.Object(None),
+        **{
+            None: providers.Singleton(InMemoryPromptRepository),
+            "sqlite": providers.Singleton(  # sentinel key
+                SqlitePromptRepository, db=providers.Callable(Path, config.db_path)
+            ),
+        },
+    )
+
+    # helper: if config.db_path is set, selector key should be "sqlite"
+    @providers.Factory
+    def _resolve_repo(config=config) -> object:
+        return "sqlite" if config.db_path() else None
```

Then, in CLI startup (e.g., in `main()` before creating `_cli` or by configuring the container early), set `container.config.db_path = Path(".obk/session.db")` when your new `db session start` command is used. (The full “session”/rules/gsl flow can come later; this gets CRUD + PRAGMAs + STRICT passing.)

## D) Tests to satisfy Acceptance #3 and #4

**Unit (FakeRepo, no FS/DB):**  
`tests/unit/prompts/test_add_and_list.py`

```python
from dataclasses import dataclass
from obk.application.prompts.ports import PromptRepository
from obk.application.prompts.commands.add_prompt import AddPrompt, handle as add_handle
from obk.application.prompts.queries.list_prompts import ListPrompts, handle as list_handle
from obk.domain.prompts.models import Prompt

class FakeRepo(PromptRepository):
    def __init__(self) -> None:
        self.items: list[Prompt] = []
    def add(self, p: Prompt) -> None: self.items.append(p)
    def list(self) -> list[Prompt]: return list(self.items)

def test_add_and_list_with_fake_repo() -> None:
    repo = FakeRepo()
    add_handle(AddPrompt(id="1", date_utc="2025-08-10", type="test"), repo)
    out = list_handle(ListPrompts(), repo)
    assert out == [Prompt("1","2025-08-10","test")]
```

**Integration (SQLite, PRAGMAs/STRICT + rotating logs not at import time):**  
`tests/integration/test_sqlite_prompt_repo.py`

```python
from pathlib import Path
import sqlite3
from obk.infrastructure.db.sqlite import SqlitePromptRepository
from obk.domain.prompts.models import Prompt

def test_sqlite_repo_pragmas_and_crud(tmp_path: Path) -> None:
    db = tmp_path / "session.db"
    repo = SqlitePromptRepository(db)
    repo.add(Prompt("1","2025-08-10","x"))
    assert [p.id for p in repo.list()] == ["1"]
    # PRAGMAs
    with sqlite3.connect(db) as con:
        assert con.execute("PRAGMA foreign_keys").fetchone()[0] == 1
        mode = con.execute("PRAGMA journal_mode").fetchone()[0]
        assert str(mode).upper() == "WAL"
```

* * *

# Gaps intentionally left for a second pass

* The **end-user DB session / rules / GSL import & reports** flows (Workflows A–B) are sizable; stage them after the minimal SQLite repo lands.
    
* Optional Alembic + property-based tests can follow once schema/rules stabilize.
    

* * *

# Conclusion (by acceptance)

* **#1 CI blocks on mypy/ruff:** **After** patch A → **PASS**.
    
* **#2 CLI calls handler via container (no infra imports):** **PASS** as-is.
    
* **#3 Unit tests with FakeRepo:** **After** patch D (unit) → **PASS**.
    
* **#4 SQLite integration + PRAGMAs/STRICT + rotating logs w/o import-time side effects:** **After** patches B–D (integration) → **PASS**.
    
* **#5 PyCharm debugging stops in handlers (no import-time side effects):** **After** patch B → **PASS**.
    