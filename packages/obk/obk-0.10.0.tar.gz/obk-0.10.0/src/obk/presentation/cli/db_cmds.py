from __future__ import annotations

import typer


def build_db_typer() -> typer.Typer:
    """Build the 'db' sub-CLI. No side effects at import time."""
    app = typer.Typer(help="Database schema and migration commands")

    # Avoid B008: predefine parameter objects, then reference them in defaults.
    rules_opt = typer.Option(
        ...,
        "--rules",
        help="Path to schema/rules YAML",
    )
    preview_opt = typer.Option(
        False,
        "--preview",
        help="Preview compiled SQL only",
    )
    apply_opt = typer.Option(
        False,
        "--apply",
        help="Apply compiled SQL",
    )

    @app.command("compile-schema")
    def compile_schema(
        rules: str = rules_opt,
        preview: bool = preview_opt,
    ) -> None:
        # Stub implementation for tests
        typer.echo(f"[stub] compile-schema rules={rules} preview={preview}")

    @app.command("migrate")
    def migrate(
        apply: bool = apply_opt,
    ) -> None:
        # Stub implementation for tests
        typer.echo(f"[stub] migrate apply={apply}")

    return app


def build_import_typer() -> typer.Typer:
    """Build the 'import' sub-CLI. No side effects at import time."""
    app = typer.Typer(help="Structured imports")

    # Avoid B008: predefine parameter objects
    files_arg = typer.Argument(
        ...,
        help="One or more GSL files",
    )
    fail_on_opt = typer.Option(
        "schema,referential",
        "--fail-on",
        help="Comma list of failure gates",
    )

    @app.command("gsl")
    def import_gsl(
        files: list[str] = files_arg,
        fail_on: str = fail_on_opt,
    ) -> None:
        # Stub implementation for tests
        typer.echo(f"[stub] import gsl files={files} fail_on={fail_on}")

    return app
