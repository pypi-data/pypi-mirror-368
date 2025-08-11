from __future__ import annotations

import os
import tomllib  # stdlib on 3.11+
from pathlib import Path

import typer


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


def _load_config() -> dict[str, str]:
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
    typer.echo(
        "❌ No project path configured. Run `obk set-project-path --here` "
        "or set OBK_PROJECT_PATH.",
        err=True,
    )
    raise typer.Exit(code=1)
