from __future__ import annotations

# Thin shim to keep the public entry points/tests stable.
# - console script: obk = "obk.cli:main"
# - tests import: from obk.cli import ObkCLI, app, main
from .presentation.cli.main import (
    ObkCLI,
    _global_excepthook,  # legacy tests might import these
    app,
    get_default_prompts_dir,
    main,
)
from .project_path import resolve_project_root

__all__ = [
    "ObkCLI",
    "app",
    "main",
    "_global_excepthook",
    "get_default_prompts_dir",
    "resolve_project_root",
]

