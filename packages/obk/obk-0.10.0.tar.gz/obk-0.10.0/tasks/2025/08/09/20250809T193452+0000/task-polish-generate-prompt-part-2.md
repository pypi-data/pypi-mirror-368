# Task: Polish `obk generate prompt` part 2

## Objective

Bring `obk generate prompt` fully in line with spec by (1) extracting project-root resolution, (2) centralizing trace-id validation, (3) ensuring sdist includes XML templates, (4) improving help with examples, and (5) adding two tests (Windows path + missing template).

## Constraints & Guardrails

* Keep public CLI surface unchanged (command names/flags).
    
* Prefer small, reviewable commits (Conventional Commits).
    
* Do not introduce new runtime deps unless strictly necessary.
    
* Preserve existing logging format and behavior.
    

## Implementation Plan

### 1) Extract project root resolution

**Add:** `src/obk/project_path.py`

```python
# src/obk/project_path.py
from __future__ import annotations
from pathlib import Path
import os
import typer
try:
    import tomllib  # py311+
except ModuleNotFoundError:  # pragma: no cover
    import tomli as tomllib  # only used if project supports <3.11

def _config_dir() -> Path:
    try:
        from platformdirs import user_config_dir
        return Path(user_config_dir("obk"))
    except Exception:  # pragma: no cover
        if os.name == "nt":
            base = Path(os.getenv("APPDATA", Path.home() / "AppData" / "Roaming"))
            return base / "obk"
        return Path.home() / ".config" / "obk"

def _config_file() -> Path:
    return _config_dir() / "config.toml"

def _load_config() -> dict:
    cfg = _config_file()
    return tomllib.loads(cfg.read_text(encoding="utf-8")) if cfg.exists() else {}

def resolve_project_root() -> Path:
    env_path = os.environ.get("OBK_PROJECT_PATH")
    if env_path:
        p = Path(env_path).expanduser()
        if not p.is_dir():
            typer.echo(f"❌ Configured project path does not exist: {p}", err=True)
            raise typer.Exit(code=1)
        return p
    cfg_path = _load_config().get("project_path")
    if cfg_path:
        p = Path(cfg_path).expanduser()
        if not p.is_dir():
            typer.echo(f"❌ Configured project path does not exist: {p}", err=True)
            raise typer.Exit(code=1)
        return p
    typer.echo("❌ No project path configured. Run `obk set-project-path --here` or set OBK_PROJECT_PATH.", err=True)
    raise typer.Exit(code=1)
```

**Change:** replace any inlined project-root logic in `src/obk/cli.py`:

```diff
- # old: local resolver in this file
- from pathlib import Path
+ from obk.project_path import resolve_project_root
...
- project_root = _resolve_project_root_inline(...)
+ project_root = resolve_project_root()
```

### 2) Centralize trace-id validation

**Edit:** `src/obk/trace_id.py`

```diff
+ import re
+
+ _TRACE_ID_RE = re.compile(r"\d{8}T\d{6}[+-]\d{4}$")
+
+ def is_valid_trace_id(value: str) -> bool:
+     return bool(_TRACE_ID_RE.fullmatch(value))
```

**Edit:** CLI command that accepts `--id`:

```diff
- if trace_id is None:
-     tid = generate_trace_id("UTC")
- elif not re.fullmatch(r"\d{8}T\d{6}[+-]\d{4}", trace_id):
+ if trace_id is None:
+     tid = generate_trace_id("UTC")
+ elif not is_valid_trace_id(trace_id):
      typer.echo(f"❌ Invalid trace id format: {trace_id}", err=True)
      raise typer.Exit(code=1)
  else:
      tid = trace_id
```

### 3) Ensure sdist includes XML templates

**Edit/Add:** `MANIFEST.in` (create if missing)

```
include README.md
include LICENSE
recursive-include src/obk/xsd *.xsd
recursive-include src/obk/templates *.xml
```

> Note: Wheel inclusion is already handled in `pyproject.toml`; this step ensures sdist parity.

### 4) Help examples (Typer help/epilog)

**Edit:** wherever the `generate` Typer app/group is defined:

```diff
- generate_app = typer.Typer(help="Generate artifacts")
+ generate_app = typer.Typer(help=(
+     "Generate artifacts\n\n"
+     "Examples:\n"
+     "  obk generate prompt\n"
+     "  obk generate prompt --date 2025-08-09\n"
+     "  obk generate prompt --id 20250809T130102+0000 --print-paths\n"
+ ))
```

### 5) Tests

**Add:** Windows path assertion (works cross-platform)

```python
# tests/test_generate_prompt_windows_paths.py
from pathlib import PureWindowsPath
from obk.trace_id import is_valid_trace_id

def test_windows_paths_format(tmp_path):
    # Simulate a known trace id and derived paths
    tid = "20250809T130102+0000"
    assert is_valid_trace_id(tid)
    win_prompt = PureWindowsPath(rf"prompts\2025\08\09\{tid}.md")
    win_task   = PureWindowsPath(rf"tasks\2025\08\09\{tid}\")
    # Pure path checks separator semantics without needing Windows
    assert "\\" in str(win_prompt)
    assert str(win_prompt).endswith(f"{tid}.md")
    assert str(win_task).endswith(f"{tid}\\")
```

**Add:** Missing template negative path

```python
# tests/test_generate_prompt_missing_template.py
import builtins
import importlib.resources as resources
import typer.testing
import obk.cli as cli

app = cli.app
runner = typer.testing.CliRunner()

def test_missing_template(monkeypatch):
    def missing_files(_pkg):
        raise FileNotFoundError("templates missing")
    monkeypatch.setattr(resources, "files", missing_files)
    result = runner.invoke(app, ["generate", "prompt", "--dry-run"])
    assert result.exit_code != 0
    assert "missing" in result.output.lower()
```

> If project targets Python <3.11, ensure `importlib_resources` backport is available or adapt the monkeypatch to your loader usage.

## Files to Touch

* `src/obk/project_path.py` (new)
    
* `src/obk/cli.py` (imports + resolver usage + help examples)
    
* `src/obk/trace_id.py` (new `is_valid_trace_id`)
    
* `MANIFEST.in` (new/updated)
    
* `tests/test_generate_prompt_windows_paths.py` (new)
    
* `tests/test_generate_prompt_missing_template.py` (new)
    

## Acceptance Criteria (DoD)

*  `obk generate prompt` behavior unchanged for happy paths.
    
*  Project root resolution lives in `obk.project_path.resolve_project_root()` and is used by CLI.
    
*  Trace-id validation uses `obk.trace_id.is_valid_trace_id()` (no regex duplication).
    
*  `sdist` contains `src/obk/templates/*.xml` (verify with `python -m build` then inspect tarball).
    
*  `obk generate` help displays the three example invocations.
    
*  New tests pass on Linux/macOS runners; PureWindowsPath test included.
    
*  CI green across supported Python versions.
    
*  No new runtime dependencies added (fallback to `tomli` only used if already in constraints or for dev).
    

## Suggested Commit Sequence

1. `refactor(project): extract resolve_project_root into obk.project_path`
    
2. `feat(trace): add is_valid_trace_id and use it in CLI`
    
3. `build(pkg): include templates in sdist via MANIFEST.in`
    
4. `docs(cli): add example invocations to generate group help`
    
5. `test(cli): add Windows path and missing-template tests`
    

## Post-Change Checks

* `pytest -q`
    
* `python -m build` then check `dist/*.tar.gz` contains `src/obk/templates/prompt.xml`
    
* Quick smoke:
    
    * `obk generate prompt --dry-run --print-paths`
        
    * `obk generate prompt --id 20250809T130102+0000 --dry-run`
        

* * *
