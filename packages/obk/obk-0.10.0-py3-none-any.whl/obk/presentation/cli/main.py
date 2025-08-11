# src/obk/presentation/cli/main.py (imports)
from __future__ import annotations

import importlib.resources
import logging
import sys
from datetime import datetime
from pathlib import Path
from types import TracebackType
from zoneinfo import ZoneInfo

import typer

from ...containers import Container
from ...harmonize import harmonize_text
from ...preprocess import postprocess_text, preprocess_text
from ...project_path import _config_file, resolve_project_root
from ...services import DivisionByZeroError, FatalError
from ...trace_id import generate_trace_id, is_valid_trace_id
from ...validation import validate_all
from .db_cmds import build_db_typer, build_import_typer
from .prompt_cmds import build_prompt_typer

LOG_FILE = Path("obk.log")


def _toml_lit(s: str) -> str:
    return "'" + s.replace("'", "''") + "'"


def _write_config(data: dict[str, str]) -> None:
    cfg = _config_file()
    cfg.parent.mkdir(parents=True, exist_ok=True)
    with cfg.open("w", encoding="utf-8") as fh:
        for key, value in data.items():
            if key == "project_path":
                fh.write(f"{key} = {_toml_lit(str(value))}\n")
            else:
                fh.write(f'{key} = "{value}"\n')


def get_default_prompts_dir(project_root: Path, timezone: str = "UTC") -> Path:
    now = datetime.now(ZoneInfo("UTC")).astimezone(ZoneInfo(timezone))
    return (
        project_root
        / "prompts"
        / f"{now.year:04}"
        / f"{now.month:02}"
        / f"{now.day:02}"
    )




def configure_logging(log_file: Path) -> None:
    """Configure root logging to write to ``log_file``."""
    from logging.handlers import RotatingFileHandler

    handler = RotatingFileHandler(
        log_file, maxBytes=1_000_000, backupCount=3, encoding="utf-8"
    )
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
        handlers=[handler],
    )


def _global_excepthook(
    exc_type: type[BaseException],
    exc_value: BaseException,
    exc_tb: TracebackType | None,
) -> None:
    """Log uncaught exceptions and exit."""
    if issubclass(exc_type, SystemExit):
        sys.__excepthook__(exc_type, exc_value, exc_tb)
        return
    logging.getLogger(__name__).critical(
        "Uncaught exception", exc_info=(exc_type, exc_value, exc_tb)
    )
    print(
        f"[FATAL] {exc_type.__name__}: {exc_value}\nSee the log for details.",
        file=sys.stderr,
    )
    sys.exit(1)


def _install_global_excepthook() -> None:
    sys.excepthook = _global_excepthook


class ObkCLI:
    """Typer-based CLI with dependency injection."""

    def __init__(
        self, log_file: Path = LOG_FILE, container: Container | None = None
    ) -> None:
        self.container = container or Container()
        self.log_file = log_file

        self.app = typer.Typer(
            add_completion=False,
            context_settings={"help_option_names": ["-h", "--help"]},
        )

        self.app.callback()(self._callback)
        self.app.command(
            name="hello-world",
            help="Print hello world",
            short_help="Print hello world",
        )(self._cmd_hello_world)
        self.app.command(
            name="divide",
            help="Divide a by b",
            short_help="Divide two numbers",
        )(self._cmd_divide)
        self.app.command(
            name="fail",
            help="Trigger a fatal error",
            short_help="Trigger a fatal error",
        )(self._cmd_fail)
        self.app.command(
            name="greet",
            help="Greet by name with optional excitement",
            short_help="Greet by name",
        )(self._cmd_greet)
        self.app.command(
            name="set-project-path",
            help="Manage project root path",
            short_help="Configure project root",
        )(self._cmd_set_project_path)
        self.app.command(
            name="validate-today",
            help="Validate today's prompt files only",
            short_help="Validate today's prompts",
        )(self._cmd_validate_today)
        self.app.command(
            name="validate-all",
            help="Validate all prompt files under prompts/",
            short_help="Validate all prompts",
        )(self._cmd_validate_all)
        self.app.command(
            name="harmonize-today",
            help="Harmonize today's prompt files only",
            short_help="Harmonize today's prompts",
        )(self._cmd_harmonize_today)
        self.app.command(
            name="harmonize-all",
            help="Harmonize all prompt files",
            short_help="Harmonize prompts",
        )(self._cmd_harmonize_all)
        self.app.command(
            name="trace-id",
            help="Generate a trace ID",
            short_help="Generate trace ID",
        )(self._cmd_trace_id)

        self.generate_app = typer.Typer(
            help=(
                "Generate artifacts\n\n"
                "Examples:\n"
                "  obk generate prompt\n"
                "  obk generate prompt --date 2025-08-09\n"
                "  obk generate prompt --id 20250809T130102+0000 --print-paths\n"
            )
        )
        self.app.add_typer(
            self.generate_app,
            name="generate",
            short_help="Generate artifacts",
        )
        self.generate_app.command(
            name="prompt",
            help="Generate prompt file and matching task folder",
            short_help="Generate prompt file",
        )(self._cmd_generate_prompt)
        self.app.command(
            name="generate-prompt",
            help="Generate prompt file and matching task folder",
            short_help="Generate prompt file",
        )(self._cmd_generate_prompt)

        self.app.add_typer(build_prompt_typer(self.container), name="prompt")
        self.app.add_typer(build_db_typer(), name="db")
        self.app.add_typer(build_import_typer(), name="import")

    
    def _callback(
        self,
        logfile: Path = typer.Option(LOG_FILE, help="Path to the log file"),
        db: Path | None = typer.Option(
            None,
            "--db",
            help="Path to SQLite DB (enables SQLite repo)",
        ),
    ) -> None:
        self.container.config.log_file.from_value(logfile)
        if db:
            self.container.config.db_path.from_value(db)

    def _cmd_hello_world(self) -> None:
        greeter = self.container.greeter()
        typer.echo(greeter.hello())

    def _cmd_divide(self, a: float, b: float) -> None:
        divider = self.container.divider()
        result = divider.divide(a, b)
        logging.getLogger(__name__).info("Divide %s by %s = %s", a, b, result)
        typer.echo(result)

    def _cmd_fail(self) -> None:
        raise FatalError("intentional failure")

    def _cmd_greet(self, name: str, excited: bool = False) -> None:
        greeter = self.container.greeter()
        typer.echo(greeter.greet(name, excited))

    def _cmd_set_project_path(
        self,
        path: Path | None = typer.Option(None, "--path", help="Set project root explicitly"),
        here: bool = typer.Option(
            False, "--here", help="Set project root to the current directory"
        ),
        unset: bool = typer.Option(False, "--unset", help="Clear the stored project root"),
        show: bool = typer.Option(False, "--show", help="Display the effective project root"),
    ) -> None:
        opts = [path is not None, here, unset, show]
        if sum(opts) != 1:
            typer.echo(
                "Specify exactly one of --path, --here, --unset, or --show",
                err=True,
            )
            raise typer.Exit(code=1)
        if show:
            root = resolve_project_root()
            typer.echo(str(root))
            raise typer.Exit(code=0)
        if unset:
            cfg = _config_file()
            if cfg.exists():
                cfg.unlink()
            typer.echo("Project path unset.")
            raise typer.Exit(code=0)
        if here:
            project_path = Path.cwd()
        else:
            assert path is not None
            project_path = Path(path).expanduser()
        if not project_path.is_dir():
            typer.echo(f"❌ Not a directory: {project_path}", err=True)
            raise typer.Exit(code=1)
        _write_config({"project_path": str(project_path)})
        typer.echo(f"Project path set to: {project_path}")
        raise typer.Exit(code=0)

    def _cmd_validate_today(
        self,
        timezone: str = typer.Option(
            "UTC", "--timezone", "-tz", help="Timezone for 'today' prompt folder (default: UTC)"
        ),
    ) -> None:
        project_root = resolve_project_root()
        prompts_dir = get_default_prompts_dir(project_root, timezone)
        typer.echo(
            f"Validating today's prompts under: {prompts_dir.resolve()} (timezone: {timezone})"
        )
        errors, passed, failed = validate_all(prompts_dir)
        if errors:
            typer.echo(f"[ERROR] Validation errors found in {failed} file(s):")
            for err in errors:
                typer.echo(f"  - {err}", err=True)
        elif passed == 0:
            typer.echo("No prompt files found.")
        else:
            typer.echo(
                f"[OK] All {passed} prompt files for today validated successfully!"
            )
        typer.echo(f"\nSummary: {passed} passed, {failed} failed.\n")
        if failed > 0:
            raise typer.Exit(code=1)
        raise typer.Exit(code=0)

    def _cmd_validate_all(
        self,
        prompts_dir: Path | None = typer.Option(
            None, help="Path to the prompts directory"
        ),
    ) -> None:
        project_root = resolve_project_root()
        if prompts_dir is None:
            prompts_dir = project_root / "prompts"
        else:
            prompts_dir = Path(prompts_dir)
        typer.echo(f"Validating ALL prompts under: {prompts_dir.resolve()}")
        errors, passed, failed = validate_all(prompts_dir)
        if errors:
            typer.echo(f"[ERROR] Validation errors found in {failed} file(s):")
            for err in errors:
                typer.echo(f"  - {err}", err=True)
        elif passed == 0:
            typer.echo("No prompt files found.")
        else:
            typer.echo("All prompt files are valid")
        typer.echo(f"\nSummary: {passed} passed, {failed} failed.\n")
        if failed > 0:
            raise typer.Exit(code=1)
        raise typer.Exit(code=0)

    def _cmd_harmonize_today(
        self,
        dry_run: bool = typer.Option(False, help="Show changes without saving"),
        timezone: str = typer.Option(
            "UTC", "--timezone", "-tz", help="Timezone for 'today' prompt folder (default: UTC)"
        ),
    ) -> None:
        project_root = resolve_project_root()
        prompts_dir = get_default_prompts_dir(project_root, timezone)
        typer.echo(
            f"Harmonizing TODAY's prompts under: {prompts_dir.resolve()} (timezone: {timezone})"
        )
        total_files = 0
        changed_files = 0
        for file_path in prompts_dir.rglob("*.md"):
            total_files += 1
            original = file_path.read_text(encoding="utf-8")
            processed, placeholders = preprocess_text(original)
            harmonized, actions = harmonize_text(processed)
            final = postprocess_text(harmonized, placeholders)
            if final != original:
                changed_files += 1
            if not dry_run and final != original:
                file_path.write_text(final, encoding="utf-8")
            if actions:
                for act in actions:
                    prefix = "Would " if dry_run else ""
                    typer.echo(f"[OK] {prefix}{act} in {file_path.name}")

        if total_files == 0:
            typer.echo("No prompt files found.")
        typer.echo(
            f"\nSummary: {changed_files if not dry_run else 0} file(s)"
            f"{' would be' if dry_run else ''} harmonized out of {total_files} checked.\n"
        )
        if dry_run:
            typer.echo("Dry run: No files were modified.\n")
        raise typer.Exit(code=0)

    def _cmd_harmonize_all(
        self,
        prompts_dir: Path | None = typer.Option(
            None, help="Path to the prompts directory"
        ),
        dry_run: bool = typer.Option(False, help="Show changes without saving"),
    ) -> None:
        project_root = resolve_project_root()
        if prompts_dir is None:
            prompts_dir = project_root / "prompts"
        else:
            prompts_dir = Path(prompts_dir)

        typer.echo(f"Harmonizing ALL prompts under: {prompts_dir.resolve()}")
        total_files = 0
        changed_files = 0
        for file_path in prompts_dir.rglob("*.md"):
            total_files += 1
            original = file_path.read_text(encoding="utf-8")
            processed, placeholders = preprocess_text(original)
            harmonized, actions = harmonize_text(processed)
            final = postprocess_text(harmonized, placeholders)
            if final != original:
                changed_files += 1
            if not dry_run and final != original:
                file_path.write_text(final, encoding="utf-8")
            if actions:
                for act in actions:
                    prefix = "Would " if dry_run else ""
                    typer.echo(f"[OK] {prefix}{act} in {file_path.name}")

        if total_files == 0:
            typer.echo("No prompt files found.")
        typer.echo(
            f"\nSummary: {changed_files if not dry_run else 0} file(s)"
            f"{' would be' if dry_run else ''} harmonized out of {total_files} checked.\n"
        )
        if dry_run:
            typer.echo("Dry run: No files were modified.\n")
        raise typer.Exit(code=0)

    def _cmd_generate_prompt(
        self,
        date: str | None = typer.Option(None, "--date", help="Override UTC date"),
        trace_id: str | None = typer.Option(
            None, "--id", help="Use specific ID; otherwise auto-generate"
        ),
        force: bool = typer.Option(False, "--force", help="Overwrite prompt file"),
        dry_run: bool = typer.Option(
            False, "--dry-run", help="Print actions; no writes"
        ),
        print_paths: bool = typer.Option(
            False, "--print-paths", help="Print abs paths for prompt + task"
        ),
    ) -> None:
        project_root = resolve_project_root()
        if date:
            try:
                dt = datetime.strptime(date, "%Y-%m-%d")
            except ValueError:
                typer.echo(
                    "❌ Invalid --date format. Expected YYYY-MM-DD (UTC).",
                    err=True,
                )
                raise typer.Exit(code=1) from None
        else:
            dt = datetime.now(ZoneInfo("UTC"))
        year = f"{dt.year:04}"
        month = f"{dt.month:02}"
        day = f"{dt.day:02}"

        if trace_id is None:
            tid = generate_trace_id("UTC")
        elif not is_valid_trace_id(trace_id):
            typer.echo(f"❌ Invalid trace id format: {trace_id}", err=True)
            raise typer.Exit(code=1)
        else:
            tid = trace_id

        prompts_dir = project_root / "prompts" / year / month / day
        tasks_dir = project_root / "tasks" / year / month / day
        prompt_file = prompts_dir / f"{tid}.md"
        task_folder = tasks_dir / tid

        # Skip collision check during dry-run
        if prompt_file.exists() and not force and not dry_run:
            typer.echo(
                f"❌ Prompt already exists: {prompt_file}. Use --force to overwrite.",
                err=True,
            )
            raise typer.Exit(code=1)

        logging.getLogger(__name__).info(
            "Generate prompt date=%s id=%s prompt=%s task=%s force=%s dry_run=%s",
            dt.date().isoformat(),
            tid,
            prompt_file,
            task_folder,
            force,
            dry_run,
        )

        # Read once so missing template surfaces even on --dry-run, and avoid re-reading later.
        template = importlib.resources.files("obk.templates").joinpath("prompt.xml").read_text(
            encoding="utf-8",
        )
        content = template.replace("__TRACE_ID__", tid)

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
        with prompt_file.open("w", encoding="utf-8", newline="\n") as fh:
            fh.write(content)

        # Output
        if print_paths:
            typer.echo(str(prompt_file.resolve()))
            typer.echo(str(task_folder.resolve()))
        else:
            typer.echo(f"✅ Created: {prompt_file.resolve()}")
            typer.echo(f"📂 Ensured: {task_folder.resolve()}")

        raise typer.Exit(code=0)

    def _cmd_trace_id(
        self,
        timezone: str = typer.Option(
            "UTC", "--timezone", "-tz", help="Timezone for trace ID generation (default: UTC)"
        ),
    ) -> None:
        typer.echo(generate_trace_id(timezone))

    def run(self, argv: list[str] | None = None) -> None:
        argv = argv or sys.argv[1:]
        try:
            cmd = typer.main.get_command(self.app)
            exit_code = cmd.main(args=argv, prog_name="obk", standalone_mode=False)
            if isinstance(exit_code, int):
                sys.exit(exit_code)
        except DivisionByZeroError as exc:
            logging.getLogger(__name__).exception("Division error")
            typer.echo(f"[ERROR] {exc}", err=True)
            sys.exit(2)


_cli = ObkCLI()
app = _cli.app

def main(argv: list[str] | None = None) -> None:
    """Entry point for ``python -m obk``."""
    argv = argv or sys.argv[1:]
    log_file = LOG_FILE
    if "--logfile" in argv:
        idx = argv.index("--logfile")
        if idx + 1 < len(argv):
            log_file = Path(argv[idx + 1])
    configure_logging(log_file)
    _install_global_excepthook()
    _cli.run(argv)


if __name__ == "__main__":
    main()

