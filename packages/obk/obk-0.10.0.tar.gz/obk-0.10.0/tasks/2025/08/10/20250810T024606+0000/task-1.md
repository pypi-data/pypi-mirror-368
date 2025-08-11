# Implementation Steps & Tests (for 20250810T024606+0000)

## 0) Pre-flight

1. Create a feature branch: `feat/cqrs-sqlite-ephemeral`.
    
2. Ensure Python 3.11+, Typer installed, and a clean venv.
    
3. Commit in small steps following the **Commit Plan** at the end.
    

* * *

## 1) Typing & linting (two-zone policy)

### 1.1 Add `py.typed`

* Create an empty file at:
    

```
src/obk/py.typed
```

### 1.2 Configure mypy & ruff in `pyproject.toml`

```toml
# pyproject.toml (add or merge)
[tool.mypy]
python_version = "3.11"
warn_unreachable = true
warn_unused_ignores = true
disallow_any_generics = true
no_implicit_optional = true
show_error_codes = true
strict_optional = true

# strict only for core packages (adjust package prefixes to match your layout)
[[tool.mypy.overrides]]
module = "obk.domain.*"
strict = true

[[tool.mypy.overrides]]
module = "obk.application.*"
strict = true

# non-strict (but enabled) at the edges
[[tool.mypy.overrides]]
module = "obk.infrastructure.*"
warn_return_any = true

[[tool.mypy.overrides]]
module = "obk.interface.*"
warn_return_any = true

[tool.ruff]
line-length = 100
select = ["E","F","I","UP","B","ANN"]
```

### 1.3 CI gate

* Ensure CI runs: `ruff`, `mypy`, `pytest -q`. Fail build on errors.
    

**Tests to add now**

* None (config only). Verify CI fails on a deliberate typing error, then revert.
    

* * *

## 2) Clean-on-top layout + vertical slices

### 2.1 Create packages

```
src/obk/
  domain/
  application/
    ports/
    commands/
    queries/
  infrastructure/
    db/
      sqlalchemy/
  interface/
    cli/
slices/
  prompts/            # first slice (example)
tests/
  unit/
  integration/
  cli/
```

### 2.2 `__init__` files

* Create `__init__.py` in each new package folder.
    

* * *

## 3) Ports & DTOs (CQRS seams)

### 3.1 DTOs and Repo Protocol

Create `src/obk/application/ports/repo.py`:

```python
from __future__ import annotations
from dataclasses import dataclass
from typing import Iterable, Optional, Protocol

@dataclass(frozen=True)
class Prompt:
    id: str
    date_utc: str
    type: str  # Literal["system","user","assistant"] optionally

@dataclass(frozen=True)
class Issue:
    id: int | None
    file: str
    location: str | None
    table: str | None
    constraint: str | None
    message: str

class Repo(Protocol):
    # Commands (writes)
    def upsert_prompt(self, p: Prompt) -> None: ...
    def record_issue(self, i: Issue) -> int: ...

    # Queries (reads)
    def get_prompt(self, pid: str) -> Optional[Prompt]: ...
    def list_prompts(self) -> Iterable[Prompt]: ...
    def list_issues(self) -> Iterable[Issue]: ...
```

**Tests to add now**

* `tests/unit/test_ports_types.py` verifying dataclass construction & type hints (mypy passes).
    

* * *

## 4) Application handlers (pure)

### 4.1 Command handler (example)

`src/obk/application/commands/add_prompt.py`:

```python
from dataclasses import dataclass
from obk.application.ports.repo import Repo, Prompt

@dataclass(frozen=True)
class AddPromptCmd:
    id: str
    date_utc: str
    type: str

def handle(cmd: AddPromptCmd, repo: Repo) -> None:
    repo.upsert_prompt(Prompt(cmd.id, cmd.date_utc, cmd.type))
```

### 4.2 Query handler (example)

`src/obk/application/queries/list_prompts.py`:

```python
from typing import Iterable
from obk.application.ports.repo import Repo, Prompt

def handle(repo: Repo) -> Iterable[Prompt]:
    return repo.list_prompts()
```

**Tests to add now**

* `tests/unit/test_handlers_prompts.py` with a `FakeRepo` (in-memory lists) to test both handlers without touching DB.
    

```python
# tests/unit/test_handlers_prompts.py
from dataclasses import dataclass
from typing import Iterable, Optional
from obk.application.commands.add_prompt import AddPromptCmd, handle as add_handle
from obk.application.queries.list_prompts import handle as list_handle
from obk.application.ports.repo import Repo, Prompt, Issue

@dataclass
class _FakeRepo(Repo):
    _prompts: dict[str, Prompt]
    _issues: list[Issue]
    def upsert_prompt(self, p: Prompt) -> None: self._prompts[p.id] = p
    def record_issue(self, i: Issue) -> int:
        self._issues.append(i); return len(self._issues)
    def get_prompt(self, pid: str) -> Optional[Prompt]: return self._prompts.get(pid)
    def list_prompts(self) -> Iterable[Prompt]: return list(self._prompts.values())
    def list_issues(self) -> Iterable[Issue]: return list(self._issues)

def test_add_and_list_prompts():
    repo = _FakeRepo({}, [])
    add_handle(AddPromptCmd("p1","2025-08-10","user"), repo)
    rows = list(list_handle(repo))
    assert len(rows) == 1 and rows[0].id == "p1"
```

* * *

## 5) DB engine (SQLite, STRICT, PRAGMAs)

### 5.1 Engine bootstrap

`src/obk/infrastructure/db/sqlalchemy/engine.py`:

```python
from __future__ import annotations
from pathlib import Path
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

def make_engine(db_path: Path) -> Engine:
    engine = create_engine(f"sqlite:///{db_path}", future=True)
    with engine.begin() as cx:
        cx.exec_driver_sql("PRAGMA foreign_keys=ON")
        cx.exec_driver_sql("PRAGMA journal_mode=WAL")
        # Base table for issues if not exists (STRICT)
        cx.execute(text("""
            CREATE TABLE IF NOT EXISTS issues(
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              file TEXT NOT NULL,
              location TEXT,
              table_name TEXT,
              constraint_name TEXT,
              message TEXT NOT NULL
            ) STRICT
        """))
    return engine
```

**Tests to add now**

* `tests/integration/test_engine_pragmas.py`:
    

```python
from pathlib import Path
from sqlalchemy import text
from obk.infrastructure.db.sqlalchemy.engine import make_engine

def test_engine_pragmas(tmp_path: Path):
    eng = make_engine(tmp_path/"session.db")
    with eng.begin() as cx:
        fk = cx.exec_driver_sql("PRAGMA foreign_keys").scalar()
        assert fk == 1
```

* * *

## 6) Repo implementation (SQLAlchemy Core)

### 6.1 Concrete repo

`src/obk/infrastructure/db/repo.py`:

```python
from __future__ import annotations
from dataclasses import dataclass
from typing import Iterable, Optional
from sqlalchemy import text
from sqlalchemy.engine import Engine
from obk.application.ports.repo import Repo, Prompt, Issue

@dataclass
class SqlRepo(Repo):
    engine: Engine

    def upsert_prompt(self, p: Prompt) -> None:
        with self.engine.begin() as cx:
            cx.execute(text("""
            CREATE TABLE IF NOT EXISTS prompts(
              id TEXT PRIMARY KEY,
              date_utc TEXT NOT NULL,
              type TEXT NOT NULL
            ) STRICT
            """))
            cx.execute(text("""
            INSERT INTO prompts(id,date_utc,type)
            VALUES(:id,:date_utc,:type)
            ON CONFLICT(id) DO UPDATE SET date_utc=excluded.date_utc, type=excluded.type
            """), dict(id=p.id, date_utc=p.date_utc, type=p.type))

    def record_issue(self, i: Issue) -> int:
        with self.engine.begin() as cx:
            res = cx.execute(text("""
            INSERT INTO issues(file,location,table_name,constraint_name,message)
            VALUES(:file,:location,:table_name,:constraint_name,:message)
            """), dict(file=i.file, location=i.location, table_name=i.table, constraint_name=i.constraint, message=i.message))
            return res.lastrowid or 0

    def get_prompt(self, pid: str) -> Optional[Prompt]:
        with self.engine.begin() as cx:
            row = cx.execute(text("SELECT id,date_utc,type FROM prompts WHERE id=:id"), {"id": pid}).mappings().first()
            return Prompt(**row) if row else None

    def list_prompts(self) -> Iterable[Prompt]:
        with self.engine.begin() as cx:
            rows = cx.execute(text("SELECT id,date_utc,type FROM prompts ORDER BY date_utc DESC")).mappings().all()
            return [Prompt(**r) for r in rows]

    def list_issues(self) -> Iterable[Issue]:
        with self.engine.begin() as cx:
            rows = cx.execute(text("""
              SELECT id, file, location, table_name AS "table", constraint_name AS "constraint", message
              FROM issues ORDER BY id ASC
            """)).mappings().all()
            return [Issue(**r) for r in rows]
```

**Tests to add now**

* `tests/integration/test_repo_prompts.py` that writes & reads prompts on a temp DB.
    
* `tests/integration/test_repo_issues.py` that inserts and lists issues.
    

* * *

## 7) Session management CLI (`db session start/end`)

### 7.1 Session util

`src/obk/infrastructure/db/session.py`:

```python
from __future__ import annotations
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

SESSION_DIR = Path(".obk")
META = SESSION_DIR / "session.meta.json"

@dataclass(frozen=True)
class SessionMeta:
    path: str
    started_at: str
    ephemeral: bool

def write_meta(db_path: Path, ephemeral: bool) -> None:
    SESSION_DIR.mkdir(parents=True, exist_ok=True)
    m = SessionMeta(str(db_path), datetime.now(timezone.utc).isoformat(), ephemeral)
    META.write_text(json.dumps(m.__dict__, indent=2), encoding="utf-8")

def read_meta() -> SessionMeta | None:
    if not META.exists(): return None
    data = json.loads(META.read_text(encoding="utf-8"))
    return SessionMeta(**data)

def clear_meta() -> None:
    if META.exists(): META.unlink()
```

### 7.2 CLI verbs

`src/obk/interface/cli/db.py`:

```python
import typer
from pathlib import Path
from obk.infrastructure.db.sqlalchemy.engine import make_engine
from obk.infrastructure.db.session import write_meta, read_meta, clear_meta
app = typer.Typer(help="Database session management")

@app.command("session-start")
def session_start(db: Path = typer.Option(Path(".obk/session.db"), "--db"),
                  ephemeral: bool = typer.Option(True, "--ephemeral/--no-ephemeral")):
    eng = make_engine(db)
    # touch engine to create file & base schema
    with eng.begin(): pass
    write_meta(db, ephemeral)
    typer.echo(f"Session started at {db} (ephemeral={ephemeral})")

@app.command("session-end")
def session_end(persist: bool = typer.Option(False, "--persist")):
    meta = read_meta()
    if not meta:
        raise typer.Exit(code=0)
    db_path = Path(meta.path)
    if meta.ephemeral and not persist and db_path.exists():
        db_path.unlink()
    clear_meta()
    typer.echo("Session ended")
```

(If you prefer `db session start/end` subcommands, register them under a parent Typer app.)

**CLI tests**

* `tests/cli/test_db_session_cli.py` using `CliRunner` to start/end and check file presence.
    

* * *

## 8) Schema compiler & migrate

### 8.1 YAML → DDL compiler

`src/obk/infrastructure/db/schema_compile.py`:

```python
from __future__ import annotations
from pathlib import Path
from typing import Any, Dict, List

import yaml

def _col_def(name: str, spec: Dict[str, Any]) -> str:
    parts = [name, spec["type"]]
    if spec.get("not_null"): parts.append("NOT NULL")
    if spec.get("pk"): parts.append("PRIMARY KEY")
    if spec.get("unique"): parts.append("UNIQUE")
    if "check" in spec: parts.append(f"CHECK ({spec['check']})")
    return " ".join(parts)

def compile_schema(yaml_path: Path) -> List[str]:
    doc = yaml.safe_load(yaml_path.read_text(encoding="utf-8")) or {}
    ddls: List[str] = []
    for tname, tdef in (doc.get("tables") or {}).items():
        cols = tdef.get("columns") or {}
        col_sql = ",\n  ".join(_col_def(k, v) for k, v in cols.items())
        strict = " STRICT" if tdef.get("strict", True) else ""
        ddls.append(f"CREATE TABLE IF NOT EXISTS {tname}(\n  {col_sql}\n){strict};")
        for idx in tdef.get("indexes", []):
            cols_csv = ",".join(idx["columns"])
            ddls.append(f"CREATE INDEX IF NOT EXISTS {idx['name']} ON {tname}({cols_csv});")
        # FKs (simple form)
        for cname, cdef in cols.items():
            ref = cdef.get("references")
            if ref:
                ddls.append(f"ALTER TABLE {tname} ADD CONSTRAINT fk_{tname}_{cname} "
                            f"FOREIGN KEY({cname}) REFERENCES {ref} ON DELETE RESTRICT;")
    return ddls
```

### 8.2 CLI wire-up

`src/obk/interface/cli/schema.py`:

```python
import typer
from pathlib import Path
from sqlalchemy import text
from obk.infrastructure.db.schema_compile import compile_schema
from obk.infrastructure.db.sqlalchemy.engine import make_engine

app = typer.Typer(help="Schema compile/migrate")

@app.command("compile")
def compile_cmd(rules: Path, preview: bool = typer.Option(False, "--preview"), db: Path = typer.Option(Path(".obk/session.db"), "--db")):
    ddls = compile_schema(rules)
    if preview:
        typer.echo("\n".join(ddls))
        return
    eng = make_engine(db)
    with eng.begin() as cx:
        for ddl in ddls:
            cx.execute(text(ddl))
    typer.echo(f"Applied {len(ddls)} statements.")
```

**Integration tests**

* `tests/integration/test_schema_compile_apply.py`:
    
    * Provide a small `db.schema.yml` in a temp dir with one table + index + FK.
        
    * Compile and apply; inspect `sqlite_master` to assert objects exist.
        

* * *

## 9) Import GSL → DB + issues

> Wire this to your existing XML validator/normalizer (names may differ). The handler should: validate → normalize → insert with a per-file transaction → on error, rollback and `record_issue`.

### 9.1 Import handler (boundary)

`src/obk/infrastructure/imports/gsl_importer.py`:

```python
from __future__ import annotations
from pathlib import Path
from typing import Iterable, Mapping
from sqlalchemy import text
from sqlalchemy.engine import Engine
from obk.application.ports.repo import Repo, Issue

def _normalize_xml_to_rows(xml_path: Path) -> Mapping[str, Iterable[Mapping[str, object]]]:
    # TODO: call your existing normalization pipeline here. Return {table_name: [rowdicts...]}
    raise NotImplementedError

def import_gsl(paths: Iterable[Path], engine: Engine, repo: Repo, fail_on: set[str]) -> int:
    failures = 0
    for p in paths:
        try:
            rows_by_table = _normalize_xml_to_rows(p)
            with engine.begin() as cx:
                for t, rows in rows_by_table.items():
                    for r in rows:
                        cols = ",".join(r.keys())
                        params = ",".join(f":{k}" for k in r.keys())
                        cx.execute(text(f"INSERT INTO {t} ({cols}) VALUES ({params})"), r)
        except Exception as ex:
            repo.record_issue(Issue(None, file=str(p), location=None, table=None, constraint=None, message=str(ex)))
            failures += 1
            if "referential" in fail_on or "schema" in fail_on:
                continue
    return failures
```

### 9.2 CLI verb

`src/obk/interface/cli/imports.py`:

```python
import typer, glob
from pathlib import Path
from obk.infrastructure.db.sqlalchemy.engine import make_engine
from obk.infrastructure.db.repo import SqlRepo
from obk.infrastructure.imports.gsl_importer import import_gsl

app = typer.Typer(help="Import pipelines")

@app.command("gsl")
def import_gsl_cmd(patterns: list[str],
                   fail_on: str = typer.Option("schema,referential", "--fail-on"),
                   db: Path = typer.Option(Path(".obk/session.db"), "--db")):
    paths = [Path(p) for pat in patterns for p in glob.glob(pat)]
    eng = make_engine(db)
    repo = SqlRepo(eng)
    failures = import_gsl(paths, eng, repo, set(x.strip() for x in fail_on.split(",") if x.strip()))
    raise typer.Exit(code=1 if failures else 0)
```

**Integration tests**

* Create minimal sample XML & a fake normalizer (monkeypatch `_normalize_xml_to_rows`) to simulate:
    
    * valid rows insert successfully,
        
    * FK/CHECK failures raise, issue recorded, non-zero exit when `--fail-on` includes the category.
        

* * *

## 10) Report commands

`src/obk/interface/cli/report.py`:

```python
import json, typer
from pathlib import Path
from obk.infrastructure.db.sqlalchemy.engine import make_engine
from obk.infrastructure.db.repo import SqlRepo

app = typer.Typer(help="Reporting")

@app.command("issues")
def issues(format: str = typer.Option("table", "--format"),
           db: Path = typer.Option(Path(".obk/session.db"), "--db")):
    repo = SqlRepo(make_engine(db))
    items = list(repo.list_issues())
    if format == "json":
        typer.echo(json.dumps([i.__dict__ for i in items], indent=2))
    else:
        for i in items:
            typer.echo(f"{i.id or ''}\t{i.file}\t{i.location or ''}\t{i.table or ''}\t{i.constraint or ''}\t{i.message}")

@app.command("summary")
def summary(format: str = typer.Option("json", "--format"),
            db: Path = typer.Option(Path(".obk/session.db"), "--db")):
    repo = SqlRepo(make_engine(db))
    items = list(repo.list_issues())
    by_file = {}
    for i in items:
        by_file.setdefault(i.file, 0); by_file[i.file] += 1
    out = {"total": len(items), "by_file": by_file}
    if format == "json": typer.echo(json.dumps(out, indent=2))
    else:
        typer.echo(f"Total issues: {out['total']}")
        for f, n in out["by_file"].items(): typer.echo(f"{f}: {n}")
```

**CLI tests**

* `tests/cli/test_reports_cli.py` to assert table and json outputs.
    

* * *

## 11) Developer scaffolding commands

### 11.1 New slice

`src/obk/interface/cli/dev.py`:

```python
import typer
from pathlib import Path

app = typer.Typer(help="Dev scaffolding")

@app.command("new-slice")
def new_slice(name: str):
    base = Path("src/obk")
    for p in [
        base/"domain"/name,
        base/"application"/name/"commands",
        base/"application"/name/"queries",
        base/"infrastructure"/name,
        base/"interface"/"cli",
        Path("slices")/name,
        Path("tests")/"slices"/name/"unit",
        Path("tests")/"slices"/name/"integration",
    ]:
        p.mkdir(parents=True, exist_ok=True)
    (Path("slices")/name/"db.schema.yml").write_text("tables: {}\n", encoding="utf-8")
    typer.echo(f"Created slice {name}")
```

### 11.2 New command/query

Add functions to `dev.py` to create handler/CLI/test skeleton files using templates.

**Tests**

* `tests/cli/test_dev_scaffold.py` to assert directories/files are created.
    

* * *

## 12) Compose the CLI

### 12.1 Root app

`src/obk/interface/cli/__init__.py`:

```python
import typer
from .db import app as db_app
from .schema import app as schema_app
from .imports import app as import_app
from .report import app as report_app
from .dev import app as dev_app

app = typer.Typer(help="obk CLI")
app.add_typer(db_app, name="db")
app.add_typer(schema_app, name="schema")
app.add_typer(import_app, name="import")
app.add_typer(report_app, name="report")
app.add_typer(dev_app, name="dev")
```

`src/obk/cli.py`:

```python
from obk.interface.cli import app

def main() -> None:
    app()
```

Ensure console_script in `pyproject.toml` points to `obk.cli:main`.

**CLI smoke test**

* `tests/cli/test_help.py`: run `obk --help` and `obk db --help`, assert command names show.
    

* * *

## 13) Logging (rotate, no import-time side effects)

`src/obk/infrastructure/logging/config.py`:

```python
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

def configure_logging(log_path: Path = Path(".obk/obk.log")) -> None:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    handler = RotatingFileHandler(log_path, maxBytes=256_000, backupCount=3)
    logging.basicConfig(level=logging.INFO, handlers=[handler])
```

Call `configure_logging()` only inside `main()` before `app()` if desired.

**Tests**

* Optional: integration test that logs rotate after exceeding size (can be skipped).
    

* * *

## 14) Acceptance runbook (matches your Workflows)

1. `obk db session start --db .obk/session.db --ephemeral`
    
2. `obk schema compile --rules obk.rules.yml`
    
3. `obk import gsl ./samples/*.xml --fail-on schema,referential`
    
4. `obk report issues --format table`
    
5. `obk report summary --format json`
    
6. `obk db session end` (deletes DB unless `--persist` used)
    

* * *

## Commit Plan (small, reviewable)

1. Typing config + `py.typed`.
    
2. Clean layout + ports + DTOs + fake repo + unit tests for handlers.
    
3. Engine + repo + session CLI + integration tests.
    
4. Schema compiler + apply; tests.
    
5. Import pipeline (stubbed normalizer) + issues; tests.
    
6. Reports; tests.
    
7. Dev scaffolding; tests.
    
8. Wire root CLI; smoke tests; docs; CI polish.
    

* * *
