<!--
Prompt-ID: <REPLACE_WITH_20250810T024606+0000>
Trace-ID:  <same_as_Prompt-ID_unless_otherwise_stated>
Task-ID:   task-<N>
Review-ID: review-<N>
Date:      <YYYY-MM-DD_from_Prompt-ID>
Paths:
  Prompt:  prompts\YYYY\MM\DD\<Prompt-ID>.md
  Tasks:   tasks\YYYY\MM\DD\<Prompt-ID>\
  Reviews: reviews\YYYY\MM\DD\<Prompt-ID>\
Rules:
  Scope:   Only consume THIS task’s content (Task-ID above) plus the prompt and the matching review(s).
  Precedence: Rules in this article are authoritative.
-->

# Task Writing Guide

Use this to turn a GSL prompt into a **deterministic, executable plan**. Keep steps small and pair **code + tests** in each step. All scoping, reference, and path rules are part of this article (no separate addendum).

---

## Implementation Steps (with tests)

### Step N — <concise title>

**Goal:** One sentence describing the outcome.

**Files:**

* ADD: `path\to\new_file.py`
* EDIT: `path\to\existing_file.py` (section or purpose)
* DELETE: *(if any)*

**Code:**

```python
# path: src\example\module.py
# brief rationale if non-obvious
<code here>
```

**Tests:**

> Co-locate step-specific tests in the same commit.

```python
# path: tests\unit\test_module.py
<test code here>
```

**Exit criteria:**

* `pytest -q` passes new tests
* `mypy` (as configured) passes in touched packages
* CLI smoke (if applicable) succeeds (e.g., `obk --help` or verb-specific check)

---

### Example (stub you can fill)

**Goal:** Add SQLite repo with PRAGMAs + STRICT and list prompts.

**Files:**

* ADD: `src\obk\infrastructure\db\sqlite.py`
* EDIT: `src\obk\containers.py` (wire repo)
* ADD: `tests\integration\test_sqlite_repo.py`

**Code:**

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
        with _connect(self._db):
            pass

    def add(self, p: Prompt) -> None:
        with _connect(self._db) as cx:
            cx.execute(
                "INSERT INTO prompts(id,date_utc,type) VALUES(?,?,?)",
                (p.id, p.date_utc, p.type),
            )

    def list(self) -> list[Prompt]:
        with _connect(self._db) as cx:
            rows = cx.execute(
                "SELECT id,date_utc,type FROM prompts ORDER BY date_utc"
            ).fetchall()
        return [Prompt(*r) for r in rows]
```

**Tests:**

```python
# path: tests\integration\test_sqlite_repo.py
from pathlib import Path
import sqlite3
from obk.infrastructure.db.sqlite import SqlitePromptRepository
from obk.domain.prompts.models import Prompt

def test_pragmas_and_crud(tmp_path: Path) -> None:
    db = tmp_path / "session.db"
    repo = SqlitePromptRepository(db)
    repo.add(Prompt("1","2025-08-10","demo"))
    assert [p.id for p in repo.list()] == ["1"]
    with sqlite3.connect(db) as cx:
        assert cx.execute("PRAGMA foreign_keys").fetchone()[0] == 1
        assert str(cx.execute("PRAGMA journal_mode").fetchone()[0]).upper() == "WAL"
```

**Exit criteria:**

* `pytest -q` passes the above test
* `mypy` clean in `obk.infrastructure.db.*`
* No import-time side effects added

---

## Tests (what good looks like)

* **Unit tests** for pure logic (handlers, DTOs, transformations). No I/O, use fakes.
* **Integration tests** for I/O (DB/files/CLI). Assert PRAGMAs, schema, exit codes, and observable artifacts.
* **CLI smoke tests** for verbs and `--help` output; assert exit code `0` and expected text.

**Minimal CLI smoke example**

```python
# path: tests\cli\test_help.py
from typer.testing import CliRunner
from obk.presentation.cli.app import app

def test_help():
    r = CliRunner().invoke(app, ["--help"])
    assert r.exit_code == 0
    assert "db" in r.stdout or "report" in r.stdout
```

---

# Prompt‑Aware Reference & Scoping Rules (Authoritative)

These rules are **source of truth** for scope and references.

## 1) Required metadata header block

Place the comment block at the very top of the document and populate it:

* `Prompt-ID` format: `^\d{8}T\d{6}\+\d{4}$` (e.g., `20250810T024606+0000`)
* `Date` = `YYYY-MM-DD` derived from the first 8 digits of `Prompt-ID`
* Paths use **backslashes** (Windows-style)

## 2) Scope Keys (drop-in under your context)

```md
### Scope Keys (Prompt-Aware)
- Prompt-ID: <…>
- Task-ID: task-<N>
- Prompt Path: prompts\YYYY\MM\DD\<Prompt-ID>.md
- Task Path: tasks\YYYY\MM\DD\<Prompt-ID>\task-<N>.md
- Reviews Dir: reviews\YYYY\MM\DD\<Prompt-ID>\
- Review Selection Rule: Only reviews whose front matter has prompt_id == Prompt-ID and task_id == Task-ID.
```

## 3) Allowed references (and nothing else)

Agents may consult only:

1. **Prompt**
   `prompts\YYYY\MM\DD\<Prompt-ID>.md`

2. **This task file only**
   `tasks\YYYY\MM\DD\<Prompt-ID>\task-<N>.md`
   ⛔ Do **not** open any other task.

3. **Matching code review(s) for this task**
   Directory: `reviews\YYYY\MM\DD\<Prompt-ID>\`
   Files: `review-*.md` that **explicitly bind** to this task via front matter:

```md
---
prompt_id: <Prompt-ID>
task_id: task-<N>
review_id: review-<K>
title: "Code review for task-<N>"
---
```

**Selection rule:** Read only reviews where `prompt_id == Prompt-ID` **and** `task_id == Task-ID`.

**Disallowed:** reviews for other tasks, any other tasks, or materials outside the current Prompt-ID tree.

## 4) Task isolation (hard constraints)

* **Single-task scope:** Execute only the current `Task-ID`.
* **Review gating:** Only reviews with matching `prompt_id` and `task_id`.
* **No cross-task inference:** If info is missing, **stop and report** the gap; do not infer from neighbor tasks.

## 5) Deterministic path patterns

* Prompt: `prompts\{YYYY}\{MM}\{DD}\{Prompt-ID}.md`
* Tasks:  `tasks\{YYYY}\{MM}\{DD}\{Prompt-ID}\task-{N}.md`
* Reviews: `reviews\{YYYY}\{MM}\{DD}\{Prompt-ID}\review-{K}.md`

`{YYYY}{MM}{DD}` are derived from `Prompt-ID`.

## 6) Pre-flight checks (must run before execution)

1. Validate `Prompt-ID` format; derive `YYYY, MM, DD`.
2. Resolve exact paths for Prompt / Task / Reviews.
3. Confirm `Task-ID` matches the filename being executed.
4. Collect only reviews whose front matter matches both IDs.
5. Refuse to proceed if any required item is missing or mismatched.

**Error message shape**

```
Missing or mismatched reference:
- prompt: OK
- task: OK (task-4.md)
- reviews: NONE MATCHING (found 2, 0 matched prompt_id+task_id)
Action: create a review with matching front matter in reviews\YYYY\MM\DD\<Prompt-ID>\
```

## 7) Precedence

If anything in other docs conflicts with this article, **use this article** and flag the conflict in your PR description.
