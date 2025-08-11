# Task: Implement `obk generate prompt` (+ alias `obk generate-prompt`)

## Objective
Create a generator command that:
- Writes a prompt file to `prompts/YYYY/MM/DD/<TRACE_ID>.xml`
- Creates a matching task folder `tasks/YYYY/MM/DD/<TRACE_ID>/`
- Uses existing trace-id logic and a **packaged** programmatic XML template

## Context
Prompts/tasks are organized by **UTC** date; trace-ids are UTC-based.
Manual stubbing causes drift. This command automates deterministic paths,
names, and a packaged template (like our XSD), working offline.

## Scope (DO change)
- Add `generate` command group and `prompt` command (+ alias `generate-prompt`)
- Add `src/obk/templates/prompt.xml` with `__TRACE_ID__` placeholder
- Include templates in wheel via `pyproject.toml`
- Write files as UTF-8 with `\n`
- Add tests covering default, date/id overrides, collision/force, dry-run, print-paths, root unset

## Out of scope (DON’T change)
- No auto-validate on generation (future `--validate`)
- No non-UTC foldering
- No additional templates

## User CLI Spec
Command(s):
- `obk generate prompt` (default pathing from UTC now)
- `obk generate-prompt` (alias)

Options:
- `--date YYYY-MM-DD` (override UTC date)
- `--id <TRACE_ID>` (use specific ID; otherwise auto-generate)
- `--force` (overwrite prompt file)
- `--dry-run` (print actions; no writes)
- `--print-paths` (print abs paths for prompt + task)

Exit codes:
- `0` success / dry-run
- Non-zero on invalid root/date/id, template load error, IO error, or collision w/o `--force`

Exact messages (use these strings):
- Root missing: `❌ No project path configured. Run \`obk set-project-path --here\` or use --path <dir>.`
- Invalid path: `❌ Configured project path does not exist: <abs-path>`
- Invalid date: `❌ Invalid --date format. Expected YYYY-MM-DD (UTC).`
- Invalid id: `❌ Invalid trace id format: <value>`
- Collision: `❌ Prompt already exists: <path>. Use --force to overwrite.`
- Success:
  - `✅ Created: <abs-prompt-file>`
  - `📂 Ensured: <abs-task-folder>`

## Files to add/modify
- ADD  `src/obk/templates/__init__.py`  (empty)
- ADD  `src/obk/templates/prompt.xml`   (programmatic template with `__TRACE_ID__`)
- MOD  `src/obk/cli.py`                 (add command + alias, wire Typer group)
- MOD  `pyproject.toml`                 (package templates; keep XSD include)
- ADD  `tests/test_generate_prompt.py`  (unit/CLI tests)

## Design details

Deterministic paths (UTC):
- Prompts: `prompts/<YYYY>/<MM>/<DD>/`
- Tasks:   `tasks/<YYYY>/<MM>/<DD>/`
- Always zero-pad `MM`, `DD`. Use UTC now if `--date` not supplied.

Trace ID:
- Import and reuse `obk.trace_id.generate_trace_id("UTC")`
- Validate `--id` via regex: `^\d{8}T\d{6}[+-]\d{4}$`
- File name and task folder must equal the ID; `<gsl-prompt id="...">` must match

Template:
- Load via `importlib.resources.files("obk.templates").joinpath("prompt.xml")`
- Replace `__TRACE_ID__` placeholder with computed/validated ID
- Write with `encoding="utf-8"`, `newline="\n"`

Project root:
- Reuse `resolve_project_root()` (already in `cli.py`); don’t duplicate code

Idempotency:
- If prompt exists w/o `--force`: error + non-zero; do not modify
- With `--force`: overwrite
- Ensure task folder exists (no error if already present)

Logging:
- INFO: UTC date, ID, created paths, flags (`--force`, `--dry-run`)

## Implementation steps (atomic)
1) Add `src/obk/templates/prompt.xml` (use the blob provided in this task’s comments).
2) Add `src/obk/templates/__init__.py` (empty file).
3) Update `pyproject.toml` wheel include to add: `src/obk/templates/*.xml`
4) In `src/obk/cli.py`:
- Import `importlib.resources` and `generate_trace_id`
- Implement `_cmd_generate_prompt(...)` per spec above
- Register under `generate` group; add flat alias `generate-prompt`
5) Add `tests/test_generate_prompt.py` (use blob in comments)
6) Run `ruff` and `pytest` (offline if needed; see below)
7) Verify help text and messages match spec exactly

## Offline testing (no internet)
If the wheelhouse is present (`dist/linux`, `dist/win`), do:
- Linux:
    ```bash
    bash scripts/offline/install-linux.sh
    bash scripts/offline/run-tests.sh
    ```

- Windows 
    ```
    
    pwsh scripts/offline/install.ps1 -Platform win
    pwsh scripts/offline/run-tests.ps1
    ```




----
----

# OBK Generate Prompt — Task, PR Template, and Attachments

Below are the complete files, ready to copy into your repo.

---

## 1) `tasks/in-use/task-generate-prompt-command.md`

```markdown
# Task: Implement `obk generate prompt` (+ alias `obk generate-prompt`)

## Objective
Create a generator command that:
- Writes a prompt file to `prompts/YYYY/MM/DD/<TRACE_ID>.md`
- Creates a matching task folder `tasks/YYYY/MM/DD/<TRACE_ID>/`
- Uses existing trace-id logic and a **packaged** programmatic XML template

## Context
Prompts/tasks are organized by **UTC** date; trace-ids are UTC-based.
Manual stubbing causes drift. This command automates deterministic paths,
names, and a packaged template (like our XSD), working offline.

## Scope (DO change)
- Add `generate` command group and `prompt` command (+ alias `generate-prompt`)
- Add `src/obk/templates/prompt.xml` with `__TRACE_ID__` placeholder
- Include templates in wheel via `pyproject.toml`
- Write files as UTF-8 with `\n`
- Add tests covering default, date/id overrides, collision/force, dry-run, print-paths, root unset

## Out of scope (DON’T change)
- No auto-validate on generation (future `--validate`)
- No non-UTC foldering
- No additional templates

## User CLI Spec
Command(s):
- `obk generate prompt` (default pathing from UTC now)
- `obk generate-prompt` (alias)

Options:
- `--date YYYY-MM-DD` (override UTC date)
- `--id <TRACE_ID>` (use specific ID; otherwise auto-generate)
- `--force` (overwrite prompt file)
- `--dry-run` (print actions; no writes)
- `--print-paths` (print abs paths for prompt + task)

Exit codes:
- `0` success / dry-run
- Non-zero on invalid root/date/id, template load error, IO error, or collision w/o `--force`

Exact messages (use these strings):
- Root missing: `❌ No project path configured. Run \`obk set-project-path --here\` or use --path <dir>.`
- Invalid path: `❌ Configured project path does not exist: <abs-path>`
- Invalid date: `❌ Invalid --date format. Expected YYYY-MM-DD (UTC).`
- Invalid id: `❌ Invalid trace id format: <value>`
- Collision: `❌ Prompt already exists: <path>. Use --force to overwrite.`
- Success:
  - `✅ Created: <abs-prompt-file>`
  - `📂 Ensured: <abs-task-folder>`

## Files to add/modify
- ADD  `src/obk/templates/__init__.py`  (empty)
- ADD  `src/obk/templates/prompt.xml`   (programmatic template with `__TRACE_ID__`)
- MOD  `src/obk/cli.py`                 (add command + alias, wire Typer group)
- MOD  `pyproject.toml`                 (package templates; keep XSD include)
- ADD  `tests/test_generate_prompt.py`  (unit/CLI tests)

## Design details

Deterministic paths (UTC):
- Prompts: `prompts/<YYYY>/<MM>/<DD>/`
- Tasks:   `tasks/<YYYY>/<MM>/<DD>/`
- Always zero-pad `MM`, `DD`. Use UTC now if `--date` not supplied.

Trace ID:
- Import and reuse `obk.trace_id.generate_trace_id("UTC")`
- Validate `--id` via regex: `^\d{8}T\d{6}[+-]\d{4}$`
- File name and task folder must equal the ID; `<gsl-prompt id="...">` must match

Template:
- Load via `importlib.resources.files("obk.templates").joinpath("prompt.xml")`
- Replace `__TRACE_ID__` placeholder with computed/validated ID
- Write with `encoding="utf-8"`, `newline="\n"`

Project root:
- Reuse `resolve_project_root()` (already in `cli.py`); don’t duplicate code

Idempotency:
- If prompt exists w/o `--force`: error + non-zero; do not modify
- With `--force`: overwrite
- Ensure task folder exists (no error if already present)

Logging:
- INFO: UTC date, ID, created paths, flags (`--force`, `--dry-run`)

## Implementation steps (atomic)
1) Add `src/obk/templates/prompt.xml` (use the blob provided in this task’s comments).
2) Add `src/obk/templates/__init__.py` (empty file).
3) Update `pyproject.toml` wheel include to add:
```

"src/obk/templates/\*.xml"

````
4) In `src/obk/cli.py`:
- Import `importlib.resources` and `generate_trace_id`
- Implement `_cmd_generate_prompt(...)` per spec above
- Register under `generate` group; add flat alias `generate-prompt`
5) Add `tests/test_generate_prompt.py` (use blob in comments)
6) Run `ruff` and `pytest` (offline if needed; see below)
7) Verify help text and messages match spec exactly

## Offline testing (no internet)
If the wheelhouse is present (`dist/linux`, `dist/win`), do:
- Linux:
```bash
bash scripts/offline/install-linux.sh
bash scripts/offline/run-tests.sh
````

* Windows:

  ```powershell
  pwsh scripts/offline/install.ps1 -Platform win
  pwsh scripts/offline/run-tests.ps1
  ```

If you need to (re)package before testing offline:

```powershell
.\scripts\package.ps1 -IncludeLinuxWheels              # uses existing dist/
# or to (re)download pinned runtime wheels first:
# .\scripts\package.ps1 -RuntimeRequirements .\requirements-offline-linux.txt -IncludeLinuxWheels
```

## Acceptance criteria (must pass)

* Default run creates both artifacts under UTC date; file/folder names equal ID; `<gsl-prompt id>` matches; exit `0`
* `--date` places under the correct UTC folder; exit `0`
* `--id` pins ID for file/folder and XML; exit `0`
* Collision w/o `--force` → non-zero; file unchanged; message includes “already exists”
* `--force` overwrites and exits `0`
* `--dry-run` prints paths, writes nothing, exit `0`
* `--print-paths` prints abs paths and creates artifacts; exit `0`
* Unset/invalid root → non-zero; clear error; no artifacts
* On Windows roots, paths are valid and prompt file is UTF-8

## Commit plan (suggested)

* `feat(generate): add packaged template + pyproject includes`
* `feat(cli): implement 'generate prompt' and alias; deterministic UTC paths`
* `test(generate): add tests for default, date/id, collision/force, dry-run, print-paths, root unset`

## Branch & PR

* Branch: `feat/generate-prompt`
* Open PR with title: `feat: add 'obk generate prompt' with deterministic UTC paths`
* Reference this task file in PR description

## Rollback

* Remove command wiring in `cli.py`
* Remove template and template include
* Delete test file
* No data migration required

## Attachments (paste into PR comment)

* **Template:** `src/obk/templates/prompt.xml` (see below)
* **Tests:** `tests/test_generate_prompt.py` (see below)
* **Init:** `src/obk/templates/__init__.py` (see below)

````

---

## 2) 
````

---

## 3) Task attachments (paste into PR comment)

> **Copy this entire block into a PR comment** so reviewers see the exact blobs.

### `src/obk/templates/prompt.xml`

```xml
<?xml version="1.0" encoding="UTF-8"?>
<gsl-prompt id="__TRACE_ID__" type="feat">
<gsl-header>
# New Prompt
</gsl-header>
<gsl-block>

<gsl-purpose>
<gsl-label>
## 1. Purpose
</gsl-label>
<gsl-description>
<!-- Describe the purpose of this prompt. -->
</gsl-description>
</gsl-purpose>

<gsl-inputs>
<gsl-label>
## 2. Inputs
</gsl-label>
<gsl-description>
<!-- List key tools, articles, or other input artifacts that guide the prompt. -->
</gsl-description>
</gsl-inputs>

<gsl-outputs>
<gsl-label>
## 3. Outputs
</gsl-label>
<gsl-description>
<!-- Define expected outputs / artifacts. -->
</gsl-description>
</gsl-outputs>

<gsl-workflows>
<gsl-label>
## 4. Workflows
</gsl-label>
<gsl-description>
<!-- How to use the outputs; user workflows. -->
</gsl-description>
</gsl-workflows>

<gsl-acceptance-tests>
<gsl-label>
## 5. Acceptance Tests
</gsl-label>

<gsl-acceptance-test id="1">
<gsl-performed-action>
<!-- When I ... -->
</gsl-performed-action>
<gsl-expected-result>
<!-- Then I expect ... -->
</gsl-expected-result>
</gsl-acceptance-test>

</gsl-acceptance-tests>

</gsl-block>
</gsl-prompt>
```

### `src/obk/templates/__init__.py`

```python
# intentionally empty; makes `obk.templates` a regular package for importlib.resources
```

### `tests/test_generate_prompt.py`

```python
import os
import re
from pathlib import Path
from typer.testing import CliRunner

from obk.cli import ObkCLI

runner = CliRunner()

def _count_artifacts(root: Path):
    prompts = list(root.glob("prompts/*/*/*/*.md"))
    tasks = list(root.glob("tasks/*/*/*/*"))
    return prompts, tasks

def test_generate_prompt_default_creates_matching_file_and_folder(tmp_path: Path, monkeypatch):
    # Arrange
    monkeypatch.setenv("OBK_PROJECT_PATH", str(tmp_path))
    app = ObkCLI().app

    # Act
    result = runner.invoke(app, ["generate", "prompt"])

    # Assert
    assert result.exit_code == 0, result.output
    prompts, tasks = _count_artifacts(tmp_path)
    assert len(prompts) == 1, f"expected 1 prompt file, got {prompts}"
    assert len(tasks) == 1, f"expected 1 task folder, got {tasks}"

    prompt_file = prompts[0]
    task_folder = tasks[0]
    assert prompt_file.stem == task_folder.name, "file/folder names must match"

    content = prompt_file.read_text(encoding="utf-8")
    assert f'id="{prompt_file.stem}"' in content

def test_generate_prompt_with_date_and_id_exact_paths(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("OBK_PROJECT_PATH", str(tmp_path))
    app = ObkCLI().app

    tid = "20250809T130102+0000"
    result = runner.invoke(app, ["generate", "prompt", "--date", "2025-08-09", "--id", tid])
    assert result.exit_code == 0, result.output

    pf = tmp_path / "prompts" / "2025" / "08" / "09" / f"{tid}.md"
    tf = tmp_path / "tasks" / "2025" / "08" / "09" / tid
    assert pf.exists(), f"missing prompt file: {pf}"
    assert tf.exists(), f"missing task folder: {tf}"
    assert f'id="{tid}"' in pf.read_text(encoding="utf-8")

def test_generate_prompt_collision_without_force_fails(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("OBK_PROJECT_PATH", str(tmp_path))
    app = ObkCLI().app

    tid = "20250809T000000+0000"
    args = ["generate", "prompt", "--date", "2025-08-09", "--id", tid]
    r1 = runner.invoke(app, args)
    assert r1.exit_code == 0, r1.output

    r2 = runner.invoke(app, args)  # same again, no --force
    assert r2.exit_code != 0, "expected non-zero on collision"
    assert "already exists" in r2.output.lower()

def test_generate_prompt_force_overwrites(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("OBK_PROJECT_PATH", str(tmp_path))
    app = ObkCLI().app

    tid = "20250809T000001+0000"
    args = ["generate", "prompt", "--date", "2025-08-09", "--id", tid]
    r1 = runner.invoke(app, args)
    assert r1.exit_code == 0, r1.output

    # Overwrite
    r2 = runner.invoke(app, args + ["--force"])
    assert r2.exit_code == 0, r2.output

def test_generate_prompt_dry_run_writes_nothing(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("OBK_PROJECT_PATH", str(tmp_path))
    app = ObkCLI().app

    r = runner.invoke(app, ["generate", "prompt", "--date", "2025-08-09", "--dry-run"])
    assert r.exit_code == 0, r.output
    prompts, tasks = _count_artifacts(tmp_path)
    assert len(prompts) == 0 and len(tasks) == 0, "dry-run should not write artifacts"

def test_generate_prompt_print_paths_outputs_two_lines(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("OBK_PROJECT_PATH", str(tmp_path))
    app = ObkCLI().app

    r = runner.invoke(app, [
        "generate", "prompt", "--date", "2025-08-09",
        "--id", "20250809T010203+0000", "--print-paths"
    ])
    assert r.exit_code == 0, r.output
    # Should print at least two lines: prompt path then task folder path
    lines = [ln for ln in r.output.splitlines() if ln.strip()]
    assert len(lines) >= 2, f"expected at least 2 lines, got: {lines[:5]}"

def test_generate_prompt_missing_root_fails(tmp_path: Path, monkeypatch):
    # Ensure env and config are not pointing to a valid project
    monkeypatch.delenv("OBK_PROJECT_PATH", raising=False)
    # isolate home/config to tmp so any user config won't be seen
    monkeypatch.setenv("HOME", str(tmp_path / "fakehome"))
    monkeypatch.setenv("USERPROFILE", str(tmp_path / "fakehome"))
    monkeypatch.setenv("APPDATA", str(tmp_path / "fakehome" / "AppData" / "Roaming"))
    (tmp_path / "fakehome").mkdir(parents=True, exist_ok=True)

    app = ObkCLI().app
    r = runner.invoke(app, ["generate", "prompt"])
    assert r.exit_code != 0, "expected non-zero when project root is unset/invalid"
    # Accept either message depending on code path:
    assert ("no project path configured" in r.output.lower()) or ("does not exist" in r.output.lower())
```

---

**Done.** Commit the PR template, and drop the attachments block into your PR description.
