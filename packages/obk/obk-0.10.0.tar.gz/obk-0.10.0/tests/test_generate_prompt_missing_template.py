import importlib.resources as resources

import typer.testing

from obk.cli import ObkCLI

app = ObkCLI().app
runner = typer.testing.CliRunner()


def test_missing_template(monkeypatch, tmp_path):
    def missing_files(_pkg):
        raise FileNotFoundError("templates missing")
    monkeypatch.setattr(resources, "files", missing_files)
    monkeypatch.setenv("OBK_PROJECT_PATH", str(tmp_path))
    result = runner.invoke(app, ["generate", "prompt", "--dry-run"])
    assert result.exit_code != 0
    assert "missing" in str(result.exception).lower()
