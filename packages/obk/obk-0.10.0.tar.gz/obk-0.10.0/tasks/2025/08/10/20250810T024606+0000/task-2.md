# Implementation Steps & Tests — 20250810T024606+0000 (Task-2)

**Goal:** Reorganize `obk` into **Clean-on-Top** folders — `domain/`, `application/`, `presentation/`, `infrastructure/` — introduce **Vertical Slice** feature folders, add a **Mediator** (MediatR-style) for CQRS, and rewire the CLI to dispatch via the mediator, all while preserving current DI.

## 0) Context & Intent

* Build on Task-1 (typing config + `py.typed`).
    
* Do **zero functional change** to existing features, only move + introduce seams.
    
* Keep `dependency-injector` as the DI container.
    

## 1) Assumptions & Constraints

* Python 3.11+, `dependency-injector` present.
    
* Packaging uses `packages = ["src/obk"]` (already set).
    
* Keep existing `obk.cli:main` entry; we’ll wrap to new `presentation` module for backward compatibility.
    

## 2) Deliverables

* New folders:  
    `src/obk/domain/`, `src/obk/application/`, `src/obk/presentation/cli/`, `src/obk/infrastructure/`.
    
* First vertical slice: `prompts` with command/query skeletons.
    
* A minimal **Mediator** with pipeline behaviors (logging stub).
    
* DI container wiring for mediator & handlers.
    
* Compatibility shims for moved modules.
    
* Unit tests for mediator dispatch + CLI smoke.
    

* * *

## 3) Implementation Steps (with tests)

### Step 1 — Create Clean + Slice folders & `__init__` files

**Files:**

* ADD folders:
    

```
src/obk/domain/
src/obk/application/
src/obk/application/prompts/commands/
src/obk/application/prompts/queries/
src/obk/presentation/cli/
src/obk/infrastructure/db/
src/obk/infrastructure/mediator/
```

* ADD empty `__init__.py` in each directory above.
    

**Exit criteria:**

* Package imports like `from obk.application import ...` succeed.
    

* * *

### Step 2 — Introduce Mediator (MediatR-style) core

**Files:**

* ADD: `src/obk/infrastructure/mediator/core.py`
    

```python
from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Callable, Dict, Protocol, TypeVar, Generic

Req = TypeVar("Req")
Res = TypeVar("Res")

class Behavior(Protocol):
    def wrap(self, next_: Callable[[Any], Any]) -> Callable[[Any], Any]: ...

@dataclass(frozen=True)
class Request: ...
@dataclass(frozen=True)
class Command(Request): ...
@dataclass(frozen=True)
class Query(Request): ...

Handler = Callable[[Any], Any]

class Mediator:
    def __init__(self, handlers: Dict[type, Handler], behaviors: list[Behavior] | None = None) -> None:
        self._handlers = handlers
        self._behaviors = list(behaviors or [])

    def send(self, request: Request) -> Any:
        req_type = type(request)
        if req_type not in self._handlers:
            raise KeyError(f"No handler registered for {req_type.__name__}")
        def invoke(req: Request) -> Any:
            return self._handlers[req_type](req)
        fn = invoke
        for b in reversed(self._behaviors):
            fn = b.wrap(fn)
        return fn(request)

# Example behavior
class LoggingBehavior:
    def __init__(self, logger: Callable[[str], None]) -> None:
        self._log = logger
    def wrap(self, next_: Callable[[Any], Any]) -> Callable[[Any], Any]:
        def _wrapped(req: Any) -> Any:
            self._log(f"[Mediator] Handling {type(req).__name__}")
            res = next_(req)
            self._log(f"[Mediator] Handled {type(req).__name__}")
            return res
        return _wrapped
```

**Tests:**

* ADD: `tests/unit/test_mediator_core.py`
    

```python
from obk.infrastructure.mediator.core import Mediator, Command, LoggingBehavior

class Ping(Command): pass

def test_mediator_dispatch(capsys):
    logs: list[str] = []
    def log(msg: str) -> None: logs.append(msg)
    def ping_handler(_: Ping) -> str: return "pong"
    m = Mediator({Ping: ping_handler}, behaviors=[LoggingBehavior(log)])
    assert m.send(Ping()) == "pong"
    assert any("Handling Ping" in s for s in logs)
```

**Exit criteria:** test passes.

* * *

### Step 3 — CQRS ports & DTOs for `prompts` slice

**Files:**

* ADD: `src/obk/application/ports.py`
    

```python
from __future__ import annotations
from dataclasses import dataclass
from typing import Iterable, Optional, Protocol

@dataclass(frozen=True)
class Prompt:
    id: str
    date_utc: str
    type: str

@dataclass(frozen=True)
class Issue:
    id: int | None
    file: str
    location: str | None
    table: str | None
    constraint: str | None
    message: str

class Repo(Protocol):
    def upsert_prompt(self, p: Prompt) -> None: ...
    def get_prompt(self, pid: str) -> Optional[Prompt]: ...
    def list_prompts(self) -> Iterable[Prompt]: ...
    def record_issue(self, i: Issue) -> int: ...
    def list_issues(self) -> Iterable[Issue]: ...
```

* ADD: `src/obk/application/prompts/commands/add_prompt.py`
    

```python
from dataclasses import dataclass
from obk.infrastructure.mediator.core import Command
from obk.application.ports import Repo, Prompt

@dataclass(frozen=True)
class AddPrompt(Command):
    id: str
    date_utc: str
    type: str

def handle(req: AddPrompt, *, repo: Repo) -> None:
    repo.upsert_prompt(Prompt(req.id, req.date_utc, req.type))
```

* ADD: `src/obk/application/prompts/queries/list_prompts.py`
    

```python
from obk.infrastructure.mediator.core import Query
from obk.application.ports import Repo, Prompt
from typing import Iterable
from dataclasses import dataclass

@dataclass(frozen=True)
class ListPrompts(Query): pass

def handle(_: ListPrompts, *, repo: Repo) -> Iterable[Prompt]:
    return repo.list_prompts()
```

**Tests:**

* ADD: `tests/unit/test_prompts_handlers.py`
    

```python
from dataclasses import dataclass
from typing import Iterable, Optional
from obk.application.ports import Repo, Prompt, Issue
from obk.application.prompts.commands.add_prompt import AddPrompt, handle as add_handle
from obk.application.prompts.queries.list_prompts import ListPrompts, handle as list_handle

@dataclass
class _FakeRepo(Repo):
    _p: dict[str, Prompt]; _i: list[Issue]
    def upsert_prompt(self, p: Prompt) -> None: self._p[p.id] = p
    def get_prompt(self, pid: str) -> Optional[Prompt]: return self._p.get(pid)
    def list_prompts(self) -> Iterable[Prompt]: return list(self._p.values())
    def record_issue(self, i: Issue) -> int: self._i.append(i); return len(self._i)
    def list_issues(self) -> Iterable[Issue]: return list(self._i)

def test_add_and_list():
    repo = _FakeRepo({}, [])
    add_handle(AddPrompt("p1", "2025-08-10", "user"), repo=repo)
    rows = list(list_handle(ListPrompts(), repo=repo))
    assert len(rows) == 1 and rows[0].id == "p1"
```

**Exit criteria:** tests pass.

* * *

### Step 4 — Integrate Mediator with DI container

**Files:**

* EDIT (or ADD if you prefer a new file): `src/obk/containers.py`  
    Wire a `Mediator` instance, registering handlers for command/query types. Example:
    

```python
from dependency_injector import containers, providers
from obk.infrastructure.mediator.core import Mediator, LoggingBehavior
from obk.application.prompts.commands.add_prompt import AddPrompt, handle as add_prompt_handle
from obk.application.prompts.queries.list_prompts import ListPrompts, handle as list_prompts_handle
from obk.application.ports import Repo

class Container(containers.DeclarativeContainer):
    config = providers.Configuration()

    # repo provider defined elsewhere; for now assume it exists:
    repo = providers.Singleton(lambda: ... )  # TODO: plug SqlRepo later

    handlers = providers.Factory(
        lambda r: {
            AddPrompt: lambda req: add_prompt_handle(req, repo=r),
            ListPrompts: lambda req: list_prompts_handle(req, repo=r),
        },
        r=repo,
    )

    mediator = providers.Singleton(
        Mediator,
        handlers=handlers,
        behaviors=[LoggingBehavior(lambda s: None)],  # replace with real logger later
    )
```

**Tests:**

* ADD: `tests/unit/test_container_mediator.py`
    

```python
from dataclasses import dataclass
from typing import Iterable, Optional
from obk.containers import Container
from obk.application.ports import Repo, Prompt, Issue
from obk.application.prompts.commands.add_prompt import AddPrompt
from obk.application.prompts.queries.list_prompts import ListPrompts

@dataclass
class _FakeRepo(Repo):
    _p: dict[str, Prompt]; _i: list[Issue]
    def upsert_prompt(self, p: Prompt) -> None: self._p[p.id] = p
    def get_prompt(self, pid: str) -> Optional[Prompt]: return self._p.get(pid)
    def list_prompts(self) -> Iterable[Prompt]: return list(self._p.values())
    def record_issue(self, i: Issue) -> int: self._i.append(i); return len(self._i)
    def list_issues(self) -> Iterable[Issue]: return list(self._i)

def test_mediator_in_container(monkeypatch):
    c = Container()
    c.repo.override(lambda: _FakeRepo({}, []))
    m = c.mediator()
    m.send(AddPrompt("p1","2025-08-10","user"))
    res = list(m.send(ListPrompts()))
    assert res and res[0].id == "p1"
```

**Exit criteria:** test passes.

* * *

### Step 5 — Move CLI to `presentation/cli` and route via mediator

**Files:**

* ADD: `src/obk/presentation/cli/main.py`
    

```python
import typer
from obk.containers import Container
from obk.application.prompts.commands.add_prompt import AddPrompt
from obk.application.prompts.queries.list_prompts import ListPrompts

app = typer.Typer(help="obk CLI")

@app.command("prompt-add")
def prompt_add(id: str, date_utc: str, type: str) -> None:
    m = Container().mediator()
    m.send(AddPrompt(id, date_utc, type))
    typer.echo("OK")

@app.command("prompt-list")
def prompt_list() -> None:
    m = Container().mediator()
    items = m.send(ListPrompts())
    for p in items:
        typer.echo(f"{p.id}\t{p.date_utc}\t{p.type}")
```

* EDIT: `src/obk/cli.py` (keep entrypoint; delegate to new app)
    

```python
from obk.presentation.cli.main import app

def main() -> None:
    app()
```

**CLI test:**

* ADD: `tests/cli/test_prompt_cli_mediator.py`
    

```python
from typer.testing import CliRunner
from obk.presentation.cli.main import app

def test_prompt_cli_help():
    r = CliRunner().invoke(app, ["--help"])
    assert r.exit_code == 0
    assert "prompt-add" in r.stdout and "prompt-list" in r.stdout
```

**Exit criteria:** CLI smoke passes; entrypoint still works.

* * *

### Step 6 — Compatibility shims for moved modules (optional but helpful)

If you moved existing modules (e.g., `preprocess`, `validation`) into layers later, create thin shims to avoid breaking imports **now**:

**Files:**

* (Example) `src/obk/preprocess.py`
    

```python
# Temporary shim for backward compatibility
from obk.infrastructure.preprocessing.preprocess import *  # noqa: F401,F403
```

**Exit criteria:** Old imports still resolve.

* * *

## 4) Acceptance Runbook

```bash
# 1) Unit tests
pytest -q tests/unit

# 2) CLI smoke
python -m obk --help
python -m obk prompt-add --help
python -m obk prompt-list --help

# 3) Mediator path
python - <<'PY'
from obk.containers import Container
from obk.application.prompts.commands.add_prompt import AddPrompt
from obk.application.prompts.queries.list_prompts import ListPrompts
m = Container().mediator()
m.send(AddPrompt("p1","2025-08-10","user"))
print([p.id for p in m.send(ListPrompts())])
PY
# expect: ['p1']
```

## 5) CI Gates

* `ruff`, `mypy`, `pytest` all run; strict in `application/` and `domain/` (as configured in Task-1).
    

## 6) Commit Plan

1. Create folders & `__init__`.
    
2. Add mediator core + tests.
    
3. Add ports + prompts handlers + tests.
    
4. Wire container mediator + tests.
    
5. Move CLI to `presentation/cli`, delegate from `obk.cli` + CLI smoke tests.
    
6. (Optional) Shims for moved modules.
    

## 7) Done When

* Clean folders exist with first slice.
    
* Mediator dispatch works with DI.
    
* CLI commands route via mediator.
    
* Tests pass and entrypoint remains stable.
    

* * *