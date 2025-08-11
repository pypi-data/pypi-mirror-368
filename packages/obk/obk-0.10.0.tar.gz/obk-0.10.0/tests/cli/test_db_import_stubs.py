from __future__ import annotations

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
