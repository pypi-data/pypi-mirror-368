---
prompt_id: 20250810T024606+0000
task_id: task-5
review_id: review-2
---
# Executive summary

You’ve nailed the **strict typing/CI gate**, **clean layering**, **SQLite infra with PRAGMAs**, and **no import-time side effects**. What’s **still missing** (or only half-there) is the **CQRS seam exposed through the CLI** and the rule-driven DB workflows (schema/rules import/migrate). In short: the building blocks are in, but the CLI isn’t yet exercising handlers through the container/mediator path.

# What’s good (meets the prompt)

* **Strict typing & package typing**
    
    * `tool.mypy` is `strict = true` with the right flags, and per-package overrides.
        
    * `src/obk/py.typed` exists and is included in the wheel build.
        
* **Lint & CI gates**
    
    * CI runs **ruff**, **mypy --strict**, and **pytest**; releases are blocked on failures.
        
* **Clean boundaries (Clean-on-top)**
    
    * CLI code (`presentation/cli/main.py`) imports **handlers**, **not infra**. Side-effects (logging + excepthook) are moved into `main()`.
        
    * `application/` has **ports** + **command/query handlers**; `domain/` has the simple model; infra adapters live under `infrastructure/`.
        
* **CQRS scaffolding present**
    
    * `application/prompts/ports.py` protocol, `commands/add_prompt.py`, `queries/list_prompts.py`, and a **Mediator** with behaviors are in place.
        
    * **Unit tests** for handlers use a fake repo; **integration test** hits the real SQLite repo and checks PRAGMAs.
        
* **SQLite bootstrap**
    
    * Connections set `PRAGMA foreign_keys=ON` and `PRAGMA journal_mode=WAL`.
        
    * Integration CRUD passes against a temp DB.
        

# Gaps / partials (what’s missing vs. the prompt)

* **CLI → Handler path (CQRS through the container)**
    
    * The CLI doesn’t currently expose a command that **sends a Command/Query via the container/mediator**. Handlers exist and are tested, but the CLI uses other services (greet/divide/harmonize) instead of invoking Add/List Prompt through the CQRS seam. This misses the “call a Typer command that triggers an application handler resolved via the container” goal.
        
* **Rule-driven schema workflow**
    
    * There’s no `db.schema.yml` / `obk.rules.yml`, nor `obk db compile-schema`, `obk db migrate`, or `obk import gsl ...` commands yet. You have the XSD and template files, but the end-to-end import/validate/report loop isn’t wired.
        
* **SQLAlchemy 2.x bootstrap**
    
    * The infra currently uses `sqlite3` directly (good for minimalism). The prompt’s plan prefers a SQLAlchemy 2.x engine bootstrap (Core is fine) so you can swap backends later. Not a blocker for now, but note the deviation.
        
* **Pre-commit**
    
    * CI gates are present; a pre-commit hook (ruff + mypy) wasn’t included. Optional, but it was in the “strict typing first” checklist.
        

# Evidence I checked (high level)

* **Typing/lint/CI:** `pyproject.toml` shows `tool.mypy` strict flags and `tool.ruff` config. The workflow runs `ruff`, `mypy --strict`, and `pytest`. `py.typed` is present and included in the wheel.
    
* **Architecture:** folders under `src/obk/` are layered: `application/`, `domain/`, `infrastructure/`, `presentation/cli/`. Container wires repos and mediator; CLI doesn’t import infra directly.
    
* **CQRS pieces:** `application/prompts/{ports,commands,queries}`, mediator with behavior, and handler unit tests with a fake repo.
    
* **SQLite & tests:** `_connect()` sets PRAGMAs; integration test asserts PRAGMAs + CRUD. Logging is configured only inside `main()` using a `RotatingFileHandler`.
    

# High-impact fixes (small changes, big wins)

1. **Expose CQRS via the CLI** (meets the “handler executes via container only” acceptance)
    
    * Add a `prompt` command group with:
        
        * `prompt add --id --type [--date UTC]` → `mediator.send(AddPrompt(...))`
            
        * `prompt list` → `mediator.send(ListPrompts())`
            
    * Keep the CLI free of infra imports; resolve the mediator from the container.
        
    
    **Minimal patch (illustrative):**
    
    ```python
    # src/obk/presentation/cli/main.py
    from ...containers import Container
    from ...application.prompts.commands.add_prompt import AddPrompt
    from ...application.prompts.queries.list_prompts import ListPrompts
    
    class ObkCLI:
        def __init__(self, log_file: Path = LOG_FILE, container: Container | None = None) -> None:
            self.container = container or Container()
            self.app = typer.Typer(add_completion=False, context_settings={"help_option_names": ["-h", "--help"]})
    
            prompt = typer.Typer(help="Prompt commands")
            self.app.add_typer(prompt, name="prompt")
    
            @prompt.command("add")
            def prompt_add(id: str, type: str, date: str = typer.Option(None, "--date", help="YYYY-MM-DD UTC")) -> None:
                if date is None:
                    date = datetime.now(ZoneInfo("UTC")).strftime("%Y-%m-%d")
                mediator = self.container.mediator()
                mediator.send(AddPrompt(id=id, date_utc=date, type=type))
                typer.echo(f"Added prompt {id} ({date}, {type})")
    
            @prompt.command("list")
            def prompt_list() -> None:
                mediator = self.container.mediator()
                items = mediator.send(ListPrompts())
                for p in items:
                    typer.echo(f"{p.id}\t{p.date_utc}\t{p.type}")
    ```
    
2. **(Optional) Add rule/schema plumbing names now, wire later**
    
    * Stubs for:
        
        * `obk db compile-schema --rules db.schema.yml --preview`
            
        * `obk db migrate --apply`
            
        * `obk import gsl <files> --fail-on schema,referential`
            
    * For a first pass, these can `typer.echo("Not yet implemented")` but establish CLI shape and acceptance hooks.
        
3. **(Optional) Pre-commit hooks**
    
    * Add `.pre-commit-config.yaml` with `ruff` + `mypy` to catch issues pre-push.
        
4. **(Later) SQLAlchemy 2.x engine shim**
    
    * Swap `_connect` to a SQLAlchemy Core engine factory (still SQLite) to align with the “engine bootstrap now, PG later” path in your plan.
        

# Acceptance test matrix (today)

* **CI blocks on type/lint** ✅ (strict mypy + ruff + pytest in CI)
    
* **Typer command triggers handler via container** ❌ (add the `prompt` group above)
    
* **Unit tests for commands/queries with FakeRepo** ✅ (present and passing approach)
    
* **Integration with SQLite PRAGMAs + CRUD; rotating logs only in entrypoint** ✅ (tests check PRAGMAs/CRUD; logging configured in `main()`)
    
* **PyCharm run/debug breaks in a handler (not CLI glue)** ◻️ (once `prompt add/list` call handlers, this becomes true; right now, CLI doesn’t hit handlers)
    

# Bottom line

You’re ~80% of the way there. Add the **`prompt` CLI group** that dispatches to handlers through the **container/mediator**, and you’ll satisfy the CQRS-through-CLI acceptance criteria and make PyCharm breakpoints land in handlers, not glue. If you want, I can generate a small PR-style patch (or a “task-1.md” per your task template) that adds those two commands and a quick CLI test.

