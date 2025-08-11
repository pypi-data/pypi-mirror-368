# Task: Polish `generate prompt` Part 3 (cleanup & test alignment)

## Objective

Apply minimal follow-ups:

1. remove duplicate `trace_id` import and regex re-check,
    
2. read the template once (before dry-run) and reuse it for the write,
    
3. make `--show` output a single deterministic line (path only),
    
4. remove a stray double assignment in `_write_config`,
    
5. align the `test_set_project_path_show` expectations.
    

## Constraints

* No CLI flag/behavior changes except `--show` prints exactly the path (one line).
    
* Keep current logging and help text intact.
    
* Keep Python compatibility and packaging as-is.
    

## Implementation Steps

### 1) `src/obk/cli.py` — imports

* Deduplicate the `trace_id` imports.
    

```diff
- from .trace_id import generate_trace_id
- from .trace_id import generate_trace_id, is_valid_trace_id
+ from .trace_id import generate_trace_id, is_valid_trace_id
```

### 2) `src/obk/cli.py` — centralize trace-id validation (no second regex)

Inside `_cmd_generate_prompt`, replace the `trace_id` branch with:

```diff
-        if trace_id is None:
-            tid = generate_trace_id("UTC")
-        elif not is_valid_trace_id(trace_id):
-            typer.echo(f"❌ Invalid trace id format: {trace_id}", err=True)
-            raise typer.Exit(code=1)
-        else:
-            if not re.fullmatch(r"\d{8}T\d{6}[+-]\d{4}", trace_id):
-                typer.echo(f"❌ Invalid trace id format: {trace_id}", err=True)
-                raise typer.Exit(code=1)
-            tid = trace_id
+        if trace_id is None:
+            tid = generate_trace_id("UTC")
+        elif not is_valid_trace_id(trace_id):
+            typer.echo(f"❌ Invalid trace id format: {trace_id}", err=True)
+            raise typer.Exit(code=1)
+        else:
+            tid = trace_id
```

### 3) `src/obk/cli.py` — read template once; reuse for write

* Load the template **before** checking `dry_run`, then reuse the same `content` for the real write (don’t re-read).
    

```diff
-        content = importlib.resources.files("obk.templates").joinpath("prompt.xml").read_text(
-            encoding="utf-8"
-        ).replace("__TRACE_ID__", tid)
+        # Read once so missing template surfaces even on --dry-run, and avoid re-reading later.
+        template = importlib.resources.files("obk.templates").joinpath("prompt.xml").read_text(
+            encoding="utf-8"
+        )
+        content = template.replace("__TRACE_ID__", tid)
@@
-        # Real writes
+        # Real writes
         prompts_dir.mkdir(parents=True, exist_ok=True)
         task_folder.mkdir(parents=True, exist_ok=True)
-        content = importlib.resources.files("obk.templates").joinpath("prompt.xml").read_text(
-            encoding="utf-8"
-        ).replace("__TRACE_ID__", tid)
         with prompt_file.open("w", encoding="utf-8", newline="\n") as fh:
             fh.write(content)
```

### 4) `src/obk/cli.py` — single-line `--show` output

```diff
-        if show:
-            root, source = resolve_project_root(with_source=True)
-            typer.echo(f"{root} (from {source})")
-            root = resolve_project_root()
-            typer.echo(str(root))
+        if show:
+            root = resolve_project_root()
+            typer.echo(str(root))
             raise typer.Exit(code=0)
```

### 5) `src/obk/cli.py` — fix stray double assignment in `_write_config`

```diff
-    cfg = _get_config_file()
-    cfg = _config_file()
+    cfg = _config_file()
```

### 6) `tests/test_project_path.py` — align `--show` expectation

In `test_set_project_path_show`, expect a **single** line containing only the path:

```diff
-    out = capsys.readouterr().out
-    assert str(project) in out
-    assert "config" in out.lower()
-    lines = [ln for ln in out.splitlines() if ln.strip()]
-    assert lines[-1].strip() == str(project)
+    out = capsys.readouterr().out
+    lines = [ln for ln in out.splitlines() if ln.strip()]
+    assert lines[-1].strip() == str(project)
```

> Leave the rest of the tests unchanged.

## Acceptance Criteria (DoD)

* `obk generate prompt` unchanged for normal use; `--dry-run` still validates presence of `prompt.xml`.
    
* Only one import line for `trace_id` in `cli.py`.
    
* No `re.fullmatch` fallback in trace-id validation path; only `is_valid_trace_id` is used.
    
* Template is read once (no second read before write).
    
* `obk set-project-path --show` prints exactly one line: the resolved path.
    
* All tests pass locally (`pytest -q`).
    
* Packaging unaffected.
    

## Commands to Run

```bash
# from repo root
pytest -q
python -m build

# quick smoke
PYTHONPATH=src OBK_PROJECT_PATH=$(pwd) python -m obk generate prompt --dry-run --print-paths
PYTHONPATH=src OBK_PROJECT_PATH=$(pwd) python -m obk generate prompt --id 20250809T130102+0000 --dry-run
```

## Suggested Commits

1. `refactor(cli): dedupe trace_id imports and simplify trace-id validation`
    
2. `perf(cli): read prompt template once and reuse for write`
    
3. `fix(cli): make --show output a single deterministic path line`
    
4. `chore(cli): remove stray double assignment in _write_config`
    
5. `test(cli): align test_set_project_path_show with single-line output`
    

* * *