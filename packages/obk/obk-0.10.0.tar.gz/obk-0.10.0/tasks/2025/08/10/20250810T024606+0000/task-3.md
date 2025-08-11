# ✅ Codex directive: fix obk repo, make tests pass

**Goal:** Make `pytest -q` pass. Clean up Ruff errors that break CI (import order, typing modernizations, long lines where easy). Keep the CLI entry point stable and tests compatible.

## 0) Prep

* Work in the project root.
    
* Assume sources under `src/`.
    

## 1) Fix the hard crash: Indentation in `src/obk/presentation/cli/main.py`

* Open `src/obk/presentation/cli/main.py`.
    
* Normalize indentation to 4 spaces everywhere (no tabs).
    
* Ensure the `class ObkCLI:` body is properly indented and **contains**:
    
    * `_callback(...)` indented one level inside the class (same level as the other `_cmd_*` methods).
        
    * No stray dedent/indent around line ~190 (where `_callback` starts).
        
* Ensure the file **ends** with exactly:
    
    ```python
    _cli = ObkCLI()
    app = _cli.app
    
    def main(argv: list[str] | None = None) -> None:
        """Entry point for ``python -m obk``."""
        _cli.run(argv)
    ```
    
* Remove any duplicate `main()` definitions (there must be **one**).
    
* Keep the existing commands/logic otherwise intact.
    

## 2) Restore a stable shim module for tests: `src/obk/cli.py`

Tests import `obk.cli` and sometimes `ObkCLI`. Replace the file contents with this minimal shim:

```python
from __future__ import annotations

# Thin shim to keep the public entry points/tests stable.
# - console script: obk = "obk.cli:main"
# - tests import: from obk.cli import ObkCLI, app, main
from .presentation.cli.main import (
    ObkCLI,
    app,
    main,
    _global_excepthook,           # legacy tests might import these
    get_default_prompts_dir,
    resolve_project_root,
)

__all__ = [
    "ObkCLI",
    "app",
    "main",
    "_global_excepthook",
    "get_default_prompts_dir",
    "resolve_project_root",
]
```

## 3) Remove duplicate class header in `src/obk/containers.py`

* If you see two consecutive lines like:
    
    ```python
    class Container(containers.DeclarativeContainer):
    class Container(containers.DeclarativeContainer):  # type: ignore[misc]
    ```
    
    delete the duplicate so only **one** `class Container(...)` remains.
    

## 4) Centralize the Prompt repository Protocol

Create `src/obk/application/prompts/ports.py`:

```python
from __future__ import annotations

from typing import Protocol

from obk.domain.prompts import Prompt


class PromptRepository(Protocol):
    def add(self, prompt: Prompt) -> None: ...
    def list(self) -> list[Prompt]: ...
```

Update handlers to **import and use** this Protocol (and remove any in-file Protocol redefinitions):

**`src/obk/application/prompts/commands/add_prompt.py`**

```python
from __future__ import annotations

from dataclasses import dataclass

from obk.domain.prompts import Prompt
from obk.infrastructure.mediator.core import Command
from .ports import PromptRepository


@dataclass(frozen=True)
class AddPrompt(Command):
    id: str
    date_utc: str
    type: str


def handle(request: AddPrompt, repo: PromptRepository) -> None:
    repo.add(Prompt(request.id, request.date_utc, request.type))
```

**`src/obk/application/prompts/queries/list_prompts.py`**

```python
from __future__ import annotations

from dataclasses import dataclass

from obk.infrastructure.mediator.core import Query
from .ports import PromptRepository


@dataclass(frozen=True)
class ListPrompts(Query):
    pass


def handle(_: ListPrompts, repo: PromptRepository):
    return repo.list()
```

## 5) Import hygiene and typing modernization

### a) `src/obk/containers.py` (imports only)

* Sort imports.
    
* Import `Callable` from `collections.abc`, not `typing`.
    

```python
from __future__ import annotations

from collections.abc import Callable
from dependency_injector import containers, providers

from .application.prompts.commands.add_prompt import AddPrompt, handle as handle_add_prompt
from .application.prompts.queries.list_prompts import ListPrompts, handle as handle_list_prompts
from .infrastructure.db.prompts import InMemoryPromptRepository
from .infrastructure.mediator.core import LoggingBehavior, Mediator
from .services import Divider, Greeter
```

### b) `src/obk/infrastructure/mediator/core.py`

* Import `Callable` from `collections.abc`.
    
* Replace `Any`/`Dict` with `object`/`dict`.
    
* Avoid `ANN401` by returning `object`.
    
* Wrap the long constructor line to ≤100 cols.
    

```python
from __future__ import annotations

from dataclasses import dataclass
from collections.abc import Callable
from typing import Protocol


@dataclass(frozen=True)
class Request: ...
@dataclass(frozen=True)
class Command(Request): ...
@dataclass(frozen=True)
class Query(Request): ...

Handler = Callable[[Request], object]


class Behavior(Protocol):
    def wrap(self, next_: Callable[[Request], object]) -> Callable[[Request], object]: ...


class Mediator:
    """Dispatch requests to handlers with optional behaviors."""

    def __init__(
        self,
        handlers: dict[type, Handler],
        behaviors: list[Behavior] | None = None,
    ) -> None:
        self._handlers = handlers
        self._behaviors = list(behaviors or [])

    def send(self, request: Request) -> object:
        req_type = type(request)
        if req_type not in self._handlers:
            raise KeyError(f"No handler registered for {req_type.__name__}")

        def invoke(req: Request) -> object:
            return self._handlers[req_type](req)

        fn: Callable[[Request], object] = invoke
        for behavior in reversed(self._behaviors):
            fn = behavior.wrap(fn)
        return fn(request)


class LoggingBehavior:
    def __init__(self, logger: Callable[[str], None]) -> None:
        self._log = logger

    def wrap(self, next_: Callable[[Request], object]) -> Callable[[Request], object]:
        def _wrapped(req: Request) -> object:
            self._log(f"[Mediator] Handling {type(req).__name__}")
            result = next_(req)
            self._log(f"[Mediator] Handled {type(req).__name__}")
            return result

        return _wrapped
```

### c) Replace deprecated `typing.List`/`typing.Tuple`

* In `src/obk/harmonize.py`, `src/obk/preprocess.py`, `src/obk/validation.py`, and `src/obk/infrastructure/db/prompts.py`:
    
    * Remove `from typing import List, Tuple`.
        
    * Use `list[...]` / `tuple[...]` in annotations.
        
    * Remove unused imports (e.g., `List` in prompts repo).
        

### d) Sort imports project-wide

* Let Ruff fix `I001` everywhere.
    

## 6) Tame a few Ruff rules without code churn

Update **pyproject.toml** to add per-file ignores:

```toml
[tool.ruff.lint.per-file-ignores]
"tests/*" = ["ANN", "E501"]
"src/obk/presentation/cli/main.py" = ["B008"]   # Typer's Option in defaults
"src/obk/validation.py" = ["B023", "E501"]      # Keep existing validation structure
```

(Keep current `select` and `line-length = 100` as-is.)

## 7) Long lines and messages

* In `src/obk/project_path.py`, wrap the very long `typer.echo(...)` error message with parentheses across lines to satisfy E501.
    
* In `validation.py`, we’re ignoring E501 per-file; no need to reflow there unless easy.
    

## 8) Repo plumbing stays the same

* Keep console script entry point: `obk = "obk.cli:main"` in `pyproject.toml`.
    
* Do **not** remove commands or behavior from the CLI; only fix indentation and hygiene.
    

## 9) Iterative fix loop (run until green)

Run this loop up to 5 times or until all pass:

```bash
# 1) Auto-fix what can be fixed
ruff check . --fix

# 2) Type-check core package only (tests often have relaxed typing)
mypy src

# 3) Run tests
pytest -q

# 4) If pytest fails:
#    - Read the first failing error, patch the minimal code to fix it,
#    - Prefer small changes over large refactors,
#    - Re-run from step 1.
```

Also verify CLI basics:

```bash
python -m obk --help
python -m obk prompt-add --help
python -m obk prompt-list --help
```

## 10) Acceptance criteria

* `pytest -q` finishes without import/indent errors and without failures.
    
* `ruff check .` is clean, except for the intended per-file ignores.
    
* `mypy src` is clean given the current `pyproject.toml`.
    
* Running `python -m obk --help` and `python -m obk prompt-... --help` works.
    

* * *
