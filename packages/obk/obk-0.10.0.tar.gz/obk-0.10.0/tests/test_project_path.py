import os
import subprocess
import sys
from pathlib import Path

import pytest
import typer

import obk.cli as cli
import obk.project_path as project_path

PYTHON = sys.executable
REPO_ROOT = Path(__file__).resolve().parents[1]


# ---------- helpers ----------

def _mk_env(tmp_path: Path) -> dict:
    """Environment for subprocess invocations (python -m obk)."""
    env = os.environ.copy()
    env["PYTHONPATH"] = str(REPO_ROOT / "src")
    env["HOME"] = str(tmp_path)
    if os.name == "nt":
        # Subprocesses sometimes ignore APPDATA for platformdirs; we still set it for completeness.
        env["APPDATA"] = str(tmp_path)
        env["LOCALAPPDATA"] = str(tmp_path)
    return env


def _isolate_env(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Isolate HOME and Windows config locations for in-process calls."""
    monkeypatch.setenv("HOME", str(tmp_path))
    if os.name == "nt":
        monkeypatch.setenv("APPDATA", str(tmp_path))
        monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))
    monkeypatch.delenv("OBK_PROJECT_PATH", raising=False)


def _monkey_cfgdir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """
    Force obk to use a deterministic config dir (bypasses platformdirs differences).
    Returns the directory; config file will be <dir>/config.toml.
    """
    cfgdir = tmp_path / "_cfgdir"
    monkeypatch.setattr(project_path, "_config_dir", lambda: cfgdir)
    return cfgdir


def _cfg_file(tmp_path: Path) -> Path:
    """Mirror project_path._config_file() after monkeypatch."""
    return tmp_path / "_cfgdir" / "config.toml"


def _win_str(p: Path) -> str:
    """Windows-style backslash string for a path (noop on non-Windows)."""
    s = str(p)
    return s.replace("/", "\\") if os.name == "nt" else s


def _run(args, env, cwd=None):
    return subprocess.run(
        [PYTHON, "-m", "obk", *args],
        capture_output=True,
        text=True,
        env=env,
        cwd=cwd,
        check=False,
    )


# ---------- tests ----------

def test_set_project_path_via_path(tmp_path, monkeypatch):
    _isolate_env(tmp_path, monkeypatch)
    _monkey_cfgdir(tmp_path, monkeypatch)  # force where config is written
    app = cli.ObkCLI(log_file=tmp_path / "log.log")

    project = tmp_path / "proj"
    project.mkdir(parents=True, exist_ok=True)

    # call command in-process (Typer exits)
    with pytest.raises(typer.Exit) as exc:
        app._cmd_set_project_path(path=project, here=False, unset=False, show=False)
    assert exc.value.exit_code == 0

    cfg = _cfg_file(tmp_path)
    assert cfg.exists()
    txt = cfg.read_text(encoding="utf-8")
    assert f"project_path = '{project}'" in txt


@pytest.mark.skipif(os.name != "nt", reason="Windows path literal test")
def test_set_project_path_windows_literal(tmp_path, monkeypatch):
    _isolate_env(tmp_path, monkeypatch)
    _monkey_cfgdir(tmp_path, monkeypatch)
    app = cli.ObkCLI(log_file=tmp_path / "log.log")

    # Create dir under tmp, but pass it with backslashes to exercise TOML literal write
    project = (tmp_path / "Work" / "obk")
    project.mkdir(parents=True, exist_ok=True)
    win_arg = Path(_win_str(project))

    with pytest.raises(typer.Exit) as exc:
        app._cmd_set_project_path(path=win_arg, here=False, unset=False, show=False)
    assert exc.value.exit_code == 0

    cfg = _cfg_file(tmp_path)
    assert cfg.exists()
    # Ensure the backslash form is preserved in TOML literal
    assert f"project_path = '{_win_str(project)}'" in cfg.read_text(encoding="utf-8")


def test_set_project_path_here(tmp_path, monkeypatch):
    _isolate_env(tmp_path, monkeypatch)
    _monkey_cfgdir(tmp_path, monkeypatch)
    app = cli.ObkCLI(log_file=tmp_path / "log.log")

    project = tmp_path / "here"
    project.mkdir(parents=True, exist_ok=True)

    # --here uses the current working directory
    monkeypatch.chdir(project)

    with pytest.raises(typer.Exit) as exc:
        app._cmd_set_project_path(path=None, here=True, unset=False, show=False)
    assert exc.value.exit_code == 0

    cfg = _cfg_file(tmp_path)
    assert cfg.exists()
    assert f"project_path = '{project}'" in cfg.read_text(encoding="utf-8")



def test_set_project_path_unset(tmp_path, monkeypatch):
    _isolate_env(tmp_path, monkeypatch)
    _monkey_cfgdir(tmp_path, monkeypatch)
    app = cli.ObkCLI(log_file=tmp_path / "log.log")

    project = tmp_path / "proj"
    project.mkdir(parents=True, exist_ok=True)

    with pytest.raises(typer.Exit) as exc:
        app._cmd_set_project_path(path=project, here=False, unset=False, show=False)
    assert exc.value.exit_code == 0

    cfg = _cfg_file(tmp_path)
    assert cfg.exists()

    with pytest.raises(typer.Exit) as exc:
        app._cmd_set_project_path(path=None, here=False, unset=True, show=False)
    assert exc.value.exit_code == 0

    assert not cfg.exists()


def test_set_project_path_show(tmp_path, monkeypatch, capsys):
    _isolate_env(tmp_path, monkeypatch)
    _monkey_cfgdir(tmp_path, monkeypatch)
    app = cli.ObkCLI(log_file=tmp_path / "log.log")

    project = tmp_path / "proj"
    project.mkdir(parents=True, exist_ok=True)

    with pytest.raises(typer.Exit):
        app._cmd_set_project_path(path=project, here=False, unset=False, show=False)

    with pytest.raises(typer.Exit) as exc:
        app._cmd_set_project_path(path=None, here=False, unset=False, show=True)
    assert exc.value.exit_code == 0

    out = capsys.readouterr().out
    lines = [ln for ln in out.splitlines() if ln.strip()]
    assert lines[-1].strip() == str(project)


def test_env_var_precedence(tmp_path, monkeypatch):
    _isolate_env(tmp_path, monkeypatch)
    _monkey_cfgdir(tmp_path, monkeypatch)

    # Write a config path...
    cfg = _cfg_file(tmp_path)
    cfg.parent.mkdir(parents=True, exist_ok=True)
    cfg_dir = tmp_path / "cfg"
    cfg_dir.mkdir(parents=True, exist_ok=True)
    cfg.write_text(f"project_path = '{cfg_dir}'\n", encoding="utf-8")

    # ...but set env to a different path, which must win.
    env_path = tmp_path / "env"
    env_path.mkdir(parents=True, exist_ok=True)
    monkeypatch.setenv("OBK_PROJECT_PATH", _win_str(env_path))

    assert cli.resolve_project_root() == env_path


def test_resolve_project_root_unset(monkeypatch, capsys, tmp_path):
    _isolate_env(tmp_path, monkeypatch)
    _monkey_cfgdir(tmp_path, monkeypatch)

    cfg = _cfg_file(tmp_path)
    if cfg.exists():
        cfg.unlink()

    with pytest.raises(typer.Exit):
        cli.resolve_project_root()
    out = capsys.readouterr().err
    assert "No project path configured" in out


def test_windows_path_env(monkeypatch, tmp_path):
    _isolate_env(tmp_path, monkeypatch)
    _monkey_cfgdir(tmp_path, monkeypatch)

    envroot = tmp_path / "envroot"
    envroot.mkdir(parents=True, exist_ok=True)

    win_env = _win_str(envroot)
    monkeypatch.setenv("OBK_PROJECT_PATH", win_env)

    path = cli.resolve_project_root()
    assert path == envroot


def test_set_project_path_invalid(tmp_path, monkeypatch):
    _isolate_env(tmp_path, monkeypatch)
    _monkey_cfgdir(tmp_path, monkeypatch)
    app = cli.ObkCLI(log_file=tmp_path / "log.log")

    missing = tmp_path / "missing"  # does not exist
    with pytest.raises(typer.Exit) as exc:
        app._cmd_set_project_path(path=missing, here=False, unset=False, show=False)
    assert exc.value.exit_code == 1


def test_configured_path_missing(monkeypatch, tmp_path, capsys):
    _isolate_env(tmp_path, monkeypatch)
    _monkey_cfgdir(tmp_path, monkeypatch)

    cfg = _cfg_file(tmp_path)
    cfg.parent.mkdir(parents=True, exist_ok=True)

    missing = tmp_path / "nope"
    cfg.write_text(f"project_path = '{missing}'\n", encoding="utf-8")

    with pytest.raises(typer.Exit) as exc:
        cli.resolve_project_root()
    assert exc.value.exit_code == 1
    err = capsys.readouterr().err
    assert f"Configured project path does not exist: {missing}" in err


def test_validate_all_requires_project_path(tmp_path, monkeypatch):
    _isolate_env(tmp_path, monkeypatch)
    _monkey_cfgdir(tmp_path, monkeypatch)

    cfg = _cfg_file(tmp_path)
    if cfg.exists():
        cfg.unlink()

    app = cli.ObkCLI(log_file=tmp_path / "log.log")
    with pytest.raises(typer.Exit) as exc:
        app._cmd_validate_all(prompts_dir=None)  # should try to resolve root and fail
    assert exc.value.exit_code == 1
