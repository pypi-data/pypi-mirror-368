# Task: Polish `generate prompt` for scripting + clarity (lean)

## Objective

Refine the existing `generate prompt` command while keeping all current behavior intact, except for a cleaner `--print-paths` output and a small parameter rename.

## What to change

### 1) CLI tweaks (`src/obk/cli.py`)

* **Parameter clarity**: rename the Python param `id` → `trace_id` (keep the flag as `--id`).
* **Scripting-friendly output**: when `--print-paths` is supplied, print **only two absolute paths** to stdout in this order:

  1. prompt file path
  2. task folder path
* **Dry-run behavior**: with `--dry-run --print-paths`, still print only those two paths and **write nothing**. Keep skipping the collision check in dry-run mode.

**Suggested structure near the end of the command:**

```python
# Skip collision check during dry-run
if prompt_file.exists() and not force and not dry_run:
    typer.echo(f"❌ Prompt already exists: {prompt_file}. Use --force to overwrite.", err=True)
    raise typer.Exit(code=1)

if dry_run:
    if print_paths:
        typer.echo(str(prompt_file.resolve()))
        typer.echo(str(task_folder.resolve()))
    else:
        typer.echo(f"Would create: {prompt_file.resolve()}")
        typer.echo(f"Would ensure: {task_folder.resolve()}")
    raise typer.Exit(code=0)

# Real writes
prompts_dir.mkdir(parents=True, exist_ok=True)
task_folder.mkdir(parents=True, exist_ok=True)
content = resources.files("obk.templates").joinpath("prompt.md").read_text(encoding="utf-8").replace("__TRACE_ID__", tid)
with prompt_file.open("w", encoding="utf-8", newline="\n") as fh:
    fh.write(content)

# Output
if print_paths:
    typer.echo(str(prompt_file.resolve()))
    typer.echo(str(task_folder.resolve()))
else:
    typer.echo(f"✅ Created: {prompt_file.resolve()}")
    typer.echo(f"📂 Ensured: {task_folder.resolve()}")
```

**Param rename snippet:**

```python
def _cmd_generate_prompt(
    self,
    date: str | None = typer.Option(None, "--date", help="Override UTC date (YYYY-MM-DD)"),
    trace_id: str | None = typer.Option(None, "--id", help="Use specific ID"),
    # ...
):
    if trace_id is None:
        tid = generate_trace_id("UTC")
    else:
        if not re.fullmatch(r"\d{8}T\d{6}[+-]\d{4}", trace_id):
            typer.echo(f"❌ Invalid trace id format: {trace_id}", err=True)
            raise typer.Exit(code=1)
        tid = trace_id
```

---

### 2) Tests (`tests/test_generate_prompt.py`)

* **Remove duplicate** `runner.invoke(...)` in the print-paths test.
* **Assert exactly two lines** for `--print-paths`.
* (Optional) Add a case for `--dry-run --print-paths` that prints two lines and writes nothing.

**Replace the print-paths test with:**

```python
def test_generate_prompt_print_paths_outputs_two_lines(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("OBK_PROJECT_PATH", str(tmp_path))
    app = ObkCLI().app

    tid = "20250809T010203+0000"
    r = runner.invoke(app, [
        "generate", "prompt",
        "--date", "2025-08-09",
        "--id", tid,
        "--print-paths",
    ])
    assert r.exit_code == 0, r.output

    lines = [ln for ln in r.output.splitlines() if ln.strip()]
    assert len(lines) == 2, f"expected exactly 2 lines, got: {lines}"

    pf = Path(lines[0]); tf = Path(lines[1])
    assert pf.exists() and tf.exists()
    assert pf.name == f"{tid}.md" and tf.name == tid
    s = str(pf).replace("\\", "/"); t = str(tf).replace("\\", "/")
    assert "prompts/2025/08/09" in s and "tasks/2025/08/09" in t
```

**Optional dry-run test:**

```python
def test_generate_prompt_dry_run_print_paths_only_two_lines_and_no_writes(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("OBK_PROJECT_PATH", str(tmp_path))
    app = ObkCLI().app

    r = runner.invoke(app, [
        "generate", "prompt",
        "--date", "2025-08-09",
        "--id", "20250809T010203+0000",
        "--dry-run",
        "--print-paths",
    ])
    assert r.exit_code == 0, r.output
    lines = [ln for ln in r.output.splitlines() if ln.strip()]
    assert len(lines) == 2

    # Ensure nothing was written
    assert not list(tmp_path.glob("prompts/*/*/*/*.md"))
    assert not list(tmp_path.glob("tasks/*/*/*/*"))
```

---

## How to run

```bash
ruff check .
pytest -q
```

> That’s it. No extra ceremony needed for a polish pass. If you do want a tiny safety net, keep a one-liner in the PR description: “`--print-paths` now outputs exactly two absolute paths; param renamed to `trace_id` (flag unchanged).\`”
