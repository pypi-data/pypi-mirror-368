<!--
Prompt-ID: 20250810T024606+0000
Trace-ID:  20250810T024606+0000
Task-ID:   task-5
Review-ID: review-2
Date:      2025-08-10
Paths:
  Prompt:  prompts\2025\08\10\20250810T024606+0000.md
  Tasks:   tasks\2025\08\10\20250810T024606+0000\
  Reviews: reviews\2025\08\10\20250810T024606+0000\
Rules:
  Scope:   Only consume THIS task’s content (Task-ID above) plus the prompt and the matching review(s).
  Precedence: Rules in this article are authoritative.
-->

# Task-5 — Expose CQRS via CLI (`prompt add`/`prompt list`) and stub DB/Import verbs

This task makes the CLI call **application handlers via the container/mediator** (acceptance gap), and adds **stub shapes** for the rule-driven DB workflow to align with the prompt (non-breaking placeholders).

---

## Implementation Steps (with tests)

### Step 1 — Add `prompt` Typer sub-app that dispatches via the mediator

**Goal:** Provide `obk prompt add` and `obk prompt list` commands that **only** interact with the application layer through `Container().mediator().send(...)`.

**Files:**

* ADD: `src\obk\presentation\cli\prompt_cmds.py`
* EDIT: `src\obk\presentation\cli\main.py` (mount the `prompt` group)

**Code:**

```python
# path: src\obk\presentation\cli\prompt_cmds.py
from __future__ import annotations

from datetime import datetime
from typing import Iterable, Sequence, cast
from zoneinfo import ZoneInfo

import typer

from ...application.prompts.commands.add_prompt import AddPrompt
from ...application.prompts.queries.list_prompts import ListPrompts
from ...containers import Container


def _today_utc_str() -> str:
    # YYYY-MM-DD in UTC to satisfy domain expectations
    return datetime.now(ZoneInfo("UTC")).strftime("%Y-%m-%d")


def build_prompt_typer(container: Container | None = None) -> typer.Typer:
    """
    Returns a Typer app wired to send CQRS commands/queries through the mediator.
    No infra imports; strictly application-facing.
    """
    c = container or Container()
    app = typer.Typer(help="Manage prompts via CQRS handlers")

    @app.command("add")
    def add(
        id: str = typer.Argument(..., help="Prompt id"),
        type: str = typer.Argument(..., help="Prompt type"),
        date: str | None = typer.Option(None, "--date", "-d", help="UTC date YYYY-MM-DD"),
    ) -> None:
        d = date or _today_utc_str()
        c.mediator().send(AddPrompt(id=id, date_utc=d, type=type))
        typer.echo(f"Added\t{id}\t{d}\t{type}")

    @app.command("list")
    def list_() -> None:
        items: Sequence[object] = c.mediator().send(ListPrompts())  # domain types, not enforced here
        for p in cast(Iterable[object], items):
            # duck-type: expects attributes id, date_utc, type
            _id = getattr(p, "id", "")
            _date = getattr(p, "date_utc", "")
            _type = getattr(p, "type", "")
            typer.echo(f"{_id}\t{_date}\t{_type}")

    return app
```

```python
# path: src\obk\presentation\cli\main.py
# Mount the new sub-app; keep all side-effects inside main()/build_app() as per clean-on-top.
from __future__ import annotations

import typer

from ...containers import Container
from .prompt_cmds import build_prompt_typer  # NEW

# Ensure a module-level Typer app is exported for tests/tools
def build_app(container: Container | None = None) -> typer.Typer:
    app = typer.Typer(add_completion=False, context_settings={"help_option_names": ["-h", "--help"]})
    # ... existing command registrations ...
    app.add_typer(build_prompt_typer(container), name="prompt")
    return app

# Export default app (used by CLI entrypoint and tests)
app: typer.Typer = build_app()
```

**Tests:**

> Co-locate step-specific tests in the same commit.

```python
# path: tests\cli\test_prompt_cli.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Sequence

from typer.testing import CliRunner

from obk.application.prompts.commands.add_prompt import AddPrompt
from obk.application.prompts.queries.list_prompts import ListPrompts
from obk.presentation.cli.prompt_cmds import build_prompt_typer


class _FakeMediator:
    def __init__(self) -> None:
        self.sent: list[object] = []
        self._list_response: Sequence[object] = []

    def send(self, msg: object) -> Any:  # mediator interface is generic
        self.sent.append(msg)
        if isinstance(msg, ListPrompts):
            return self._list_response
        return None

    def set_list_response(self, items: Sequence[object]) -> None:
        self._list_response = items


class _FakeContainer:
    def __init__(self, mediator: _FakeMediator) -> None:
        self._m = mediator

    def mediator(self) -> _FakeMediator:
        return self._m


@dataclass
class _PromptRow:
    id: str
    date_utc: str
    type: str


def test_prompt_add_dispatches_command() -> None:
    m = _FakeMediator()
    c = _FakeContainer(m)
    app = build_prompt_typer(c)
    r = CliRunner().invoke(app, ["add", "p-1", "demo", "--date", "2025-08-10"])
    assert r.exit_code == 0, r.stdout
    assert any(isinstance(s, AddPrompt) for s in m.sent)
    sent = next(s for s in m.sent if isinstance(s, AddPrompt))
    assert (sent.id, sent.date_utc, sent.type) == ("p-1", "2025-08-10", "demo")


def test_prompt_list_prints_items_from_query() -> None:
    m = _FakeMediator()
    m.set_list_response([_PromptRow("a", "2025-08-09", "x"), _PromptRow("b", "2025-08-10", "y")])
    c = _FakeContainer(m)
    app = build_prompt_typer(c)
    r = CliRunner().invoke(app, ["list"])
    assert r.exit_code == 0, r.stdout
    assert "a\t2025-08-09\tx" in r.stdout
    assert "b\t2025-08-10\ty" in r.stdout
```

**Exit criteria:**

* `pytest -q` passes the new tests.
* `mypy` (as configured) passes in `obk.presentation.cli.*`.
* No infra imports from CLI; commands dispatch only through `container.mediator().send(...)`.

---

### Step 2 — Mount `prompt` group in top-level CLI and smoke-test help

**Goal:** Ensure the main CLI exposes the new `prompt` verbs.

**Files:**

* EDIT: `src\obk\presentation\cli\main.py` (already mounted in Step 1)
* ADD:  `tests\cli\test_prompt_group_help.py`

**Code:** *(no additional code beyond Step 1 edit)*

**Tests:**

```python
# path: tests\cli\test_prompt_group_help.py
from typer.testing import CliRunner
from obk.presentation.cli.main import app

def test_prompt_group_visible_in_help() -> None:
    r = CliRunner().invoke(app, ["--help"])
    assert r.exit_code == 0
    # Typer prints subcommands in help; ensure "prompt" group is there
    assert "prompt" in r.stdout
```

**Exit criteria:**

* `pytest -q` passes.
* `obk --help` (or module-invoked equivalent) shows `prompt` in output.

---

### Step 3 — Add **stubs** for rule-driven DB workflow commands (non-breaking placeholders)

**Goal:** Establish CLI shape for DB schema/import workflow per the prompt, returning success with a clear “Not implemented yet” message.

**Files:**

* ADD: `src\obk\presentation\cli\db_cmds.py`
* EDIT: `src\obk\presentation\cli\main.py` (mount `db` and `import` groups)
* ADD: `tests\cli\test_db_import_stubs.py`

**Code:**

```python
# path: src\obk\presentation\cli\db_cmds.py
from __future__ import annotations

import typer

def build_db_typer() -> typer.Typer:
    app = typer.Typer(help="Database schema and migration commands")

    @app.command("compile-schema")
    def compile_schema(
        rules: str = typer.Option(..., "--rules", help="Path to schema/rules YAML"),
        preview: bool = typer.Option(False, "--preview", help="Preview compiled SQL only"),
    ) -> None:
        typer.echo(f"[stub] compile-schema rules={rules} preview={preview}")

    @app.command("migrate")
    def migrate(apply: bool = typer.Option(False, "--apply", help="Apply migration")) -> None:
        typer.echo(f"[stub] migrate apply={apply}")

    return app


def build_import_typer() -> typer.Typer:
    app = typer.Typer(help="Structured imports")
    @app.command("gsl")
    def import_gsl(
        files: list[str] = typer.Argument(..., help="One or more GSL files"),
        fail_on: str = typer.Option("schema,referential", "--fail-on", help="Comma list of failure gates"),
    ) -> None:
        typer.echo(f"[stub] import gsl files={files} fail_on={fail_on}")
    return app
```

```python
# path: src\obk\presentation\cli\main.py
from .db_cmds import build_db_typer, build_import_typer  # NEW

def build_app(container: Container | None = None) -> typer.Typer:
    app = typer.Typer(add_completion=False, context_settings={"help_option_names": ["-h", "--help"]})
    # ... existing command registrations ...
    app.add_typer(build_prompt_typer(container), name="prompt")
    app.add_typer(build_db_typer(), name="db")         # NEW
    app.add_typer(build_import_typer(), name="import") # NEW
    return app
```

**Tests:**

```python
# path: tests\cli\test_db_import_stubs.py
from typer.testing import CliRunner
from obk.presentation.cli.main import app

def test_db_compile_schema_stub() -> None:
    r = CliRunner().invoke(app, ["db", "compile-schema", "--rules", "db.schema.yml", "--preview"])
    assert r.exit_code == 0
    assert "[stub] compile-schema" in r.stdout

def test_db_migrate_stub() -> None:
    r = CliRunner().invoke(app, ["db", "migrate", "--apply"])
    assert r.exit_code == 0
    assert "[stub] migrate" in r.stdout

def test_import_gsl_stub() -> None:
    r = CliRunner().invoke(app, ["import", "gsl", "a.gsl", "b.gsl", "--fail-on", "schema"])
    assert r.exit_code == 0
    assert "[stub] import gsl" in r.stdout
```

**Exit criteria:**

* `pytest -q` passes new tests.
* `mypy` passes for `obk.presentation.cli.db_cmds`.
* CLI help shows `db` and `import` groups.

---

## Global Exit Criteria

* `pytest -q` passes all new tests.
* `mypy` (repo-configured) passes on touched packages.
* Running:

  * `python -m obk.presentation.cli.main --help` includes `prompt`, `db`, and `import`.
  * `python -m obk.presentation.cli.main prompt add p-1 demo --date 2025-08-10` returns exit code `0`.
  * `python -m obk.presentation.cli.main prompt list` returns exit code `0` (even if empty).

---

## Notes & Constraints

* **CQRS seam only**: The CLI must not import infrastructure; all work flows through `container.mediator().send(...)`.
* **Rule-workflow stubs**: Intentionally non-functional but shape-stable to unblock docs/tests and future wiring.
* Keep logging/excepthook confined to the entrypoint; no import-time side effects.

```md
### Scope Keys (Prompt-Aware)
- Prompt-ID: 20250810T024606+0000
- Task-ID: task-5
- Prompt Path: prompts\2025\08\10\20250810T024606+0000.md
- Task Path: tasks\2025\08\10\20250810T024606+0000\task-5.md
- Reviews Dir: reviews\2025\08\10\20250810T024606+0000\
- Review Selection Rule: Only reviews whose front matter has prompt_id == Prompt-ID and task_id == Task-ID.
```

### Pre-flight checks (must run before execution)

1. Validate `Prompt-ID` format; derive `YYYY, MM, DD`.
2. Resolve exact paths for Prompt / Task / Reviews.
3. Confirm `Task-ID` matches the filename being executed.
4. Collect only reviews whose front matter matches both IDs.
5. Refuse to proceed if any required item is missing or mismatched.

**Error message shape**

```
Missing or mismatched reference:
- prompt: OK
- task: OK (task-5.md)
- reviews: NONE MATCHING (found N, 0 matched prompt_id+task_id)
Action: create a review with matching front matter in reviews\2025\08\10\20250810T024606+0000\
```
