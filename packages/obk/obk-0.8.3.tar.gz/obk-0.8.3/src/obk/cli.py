from __future__ import annotations

import sys
import logging
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo

import typer

from .containers import Container
from .services import DivisionByZeroError, FatalError
from .trace_id import generate_trace_id
from .validation import validate_all
from .preprocess import preprocess_text, postprocess_text
from .harmonize import harmonize_text

REPO_ROOT = Path(__file__).resolve().parents[2]
# Default log file path is relative to the current working directory
LOG_FILE = Path("obk.log")


def get_default_prompts_dir(timezone: str = "UTC"):
    now = datetime.now(ZoneInfo("UTC")).astimezone(ZoneInfo(timezone))
    return (
        REPO_ROOT
        / "prompts"
        / f"{now.year:04}"
        / f"{now.month:02}"
        / f"{now.day:02}"
    )


def find_prompts_root() -> Path:
    """Search upwards from CWD for the 'prompts' directory."""
    cwd = Path.cwd()
    for parent in [cwd] + list(cwd.parents):
        candidate = parent / "prompts"
        if candidate.is_dir():
            return candidate
    raise FileNotFoundError(
        "Could not find 'prompts' directory. Please run this command from within your project tree."
    )


def configure_logging(log_file: Path) -> None:
    """Configure root logging to write to ``log_file``."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
        handlers=[logging.FileHandler(log_file, encoding="utf-8")],
    )


def _global_excepthook(
    exc_type: type[BaseException], exc_value: BaseException, exc_tb
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

    def _callback(
        self, logfile: Path = typer.Option(LOG_FILE, help="Path to the log file")
    ) -> None:
        self.container.config.log_file.from_value(logfile)
        configure_logging(self.container.config.log_file())

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

    def _cmd_validate_today(
        self,
        timezone: str = typer.Option(
            "UTC", "--timezone", "-tz", help="Timezone for 'today' prompt folder (default: UTC)"
        ),
    ) -> None:
        prompts_dir = get_default_prompts_dir(timezone)
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
        if prompts_dir is None:
            try:
                prompts_dir = find_prompts_root()
            except FileNotFoundError as e:
                typer.echo(f"[ERROR] {e}", err=True)
                raise typer.Exit(code=2)
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
        prompts_dir = get_default_prompts_dir(timezone)
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
        if prompts_dir is None:
            try:
                prompts_dir = find_prompts_root()
            except FileNotFoundError as e:
                typer.echo(f"[ERROR] {e}", err=True)
                raise typer.Exit(code=2)
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


def main(argv: list[str] | None = None) -> None:
    """Entry point for ``python -m obk``."""
    ObkCLI().run(argv)
