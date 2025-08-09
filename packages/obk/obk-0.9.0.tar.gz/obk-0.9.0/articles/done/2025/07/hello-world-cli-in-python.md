# How to Write a Scalable 'Hello World' CLI in Python

> _Learn how to scaffold a command‑line tool that starts as a simple “hello‑world” but is ready to grow into a production‑grade, distributable package._

* * *

## 1  Why start with “scalable” in mind?

A command‑line interface that **begins small** but **anticipates growth** pays off later—especially when:

* multiple sub‑commands will eventually be added,
    
* you need isolated unit tests and CI,
    
* you plan to publish wheels to PyPI or run the tool inside containers or serverless functions.
    

By adopting the modern Python packaging standards (PEP 517/518 and PEP 621) **now**, you avoid painful rewrites later.

* * *

## 2  Technology choices

| Concern | Modern, best‑in‑class choice | Why |
| --- | --- | --- |
| CLI framework | **Typer** | Click‑compatible, type‑annotated, async‑friendly |
| Test framework | **pytest** | Ubiquitous, rich plugin ecosystem |
| Packaging/build backend | **Hatchling** (via **Hatch**) | Fast, PEP 517‑native, simple config |
| Lint / formatting (optional) | Ruff + Black | Instant feedback, zero‑config defaults |
| CI template | GitHub Actions | Free for open‑source, easy PyPI/coverage/pip audit jobs |

Feel free to swap in Poetry, PDM, or Flit if they fit your workflow better—the skeleton below stays valid.

* * *

## 3  Project skeleton

```text
disney-cli/
├── .gitignore
├── MANIFEST.in
├── pyproject.toml
├── README.md
├── src/
│   └── disney/
│       ├── __init__.py
│       ├── __main__.py      # deployment shim
│       └── cli.py           # Typer app lives here
└── tests/
    └── test_cli.py
```

### `.gitignore`

Start with the **official Python.gitignore** from GitHub:

```
# Byte‑compiled / optimized / DLL files
__pycache__/
*.py[cod]
*.so
# Distribution / packaging
build/
dist/
*.egg-info/
.eggs/
# …
```

Copy the latest template or add it as a sub‑file with `curl https://raw.githubusercontent.com/github/gitignore/main/Python.gitignore -o .gitignore`.

* * *

## 4  Coding the minimal CLI

`src/disney/cli.py`

```python
from typer import Typer, echo

app = Typer(add_completion=False)  # completions wired via Click ≥8 automatically

@app.command()
def hello(name: str = "world"):
    """A stub command that prints a friendly greeting."""
    echo(f"Hello, {name}!")

# More sub‑commands will slot in here as the project grows
```

`src/disney/__init__.py`

```python
__all__ = ["__version__", "cli"]
__version__ = "0.1.0"
```

### Deployment shim (`python -m disney`)

`src/disney/__main__.py`

```python
from .cli import app

if __name__ == "__main__":
    # This makes `python -m disney` behave exactly like the installed console‑script
    app()
```

* * *

## 5  Packaging with `pyproject.toml`

```toml
[build-system]
requires = ["hatchling>=1.24"]
build-backend = "hatchling.build"

[project]
name = "disney-cli"
version = "0.1.0"
description = "A scalable hello‑world CLI starter."
authors = [{ name = "Your Name", email = "you@example.com" }]
readme = "README.md"
requires-python = ">=3.9"

dependencies = ["typer[all]>=0.12"]

[project.scripts]
disney = "disney.cli:app"

[tool.hatch.build.targets.wheel]
packages = ["src/disney"]

[tool.hatch.envs.default]
dependencies = [
  "pytest",
  "ruff",     # optional linting
  "black",    # optional formatting
]

[tool.pytest.ini_options]
addopts = "-q"
```

What this buys you:

* **Standard‑compliant build**: `python -m build` (or `hatch build`) creates both wheel and sdist.
    
* **Console‑script**: The `[project.scripts]` table registers `disney` on `$PATH` after `pip install .`.
    

### `MANIFEST.in`

Include extra files not automatically packaged by Hatchling:

```
include README.md
include LICENSE
```

* * *

## 6  Unit tests with pytest

`tests/test_cli.py`

```python
from typer.testing import CliRunner
from disney.cli import app

runner = CliRunner()

def test_hello_default():
    result = runner.invoke(app, ["hello"])
    assert result.exit_code == 0
    assert "Hello, world!" in result.output

def test_hello_custom():
    result = runner.invoke(app, ["hello", "Alice"])
    assert result.exit_code == 0
    assert "Hello, Alice!" in result.output
```

Run them locally:

```bash
hatch env run pytest          # or just `pytest` inside an activated venv
```

* * *

## 7  The deployment shim explained

Because you shipped **both**:

1. **A console‑script** (`disney`) installed via entry points, **and**
    
2. **An executable module** (`python -m disney`),
    

you gain flexibility:

* **Inside containers/zipapps** where the entry‑point wrapper may not exist, `python -m disney` still works.
    
* Users who clone the repo can run the CLI without installing: `python -m src.disney`.
    

* * *

## 8  Quality‑of‑life extras (optional but recommended)

1. **Pre‑commit hooks**
    
    ```bash
    pre-commit install -t pre-commit -t pre-push
    ```
    
    Sample `.pre-commit-config.yaml`:
    
    ```yaml
    repos:
      - repo: https://github.com/astral-sh/ruff-pre-commit
        rev: v0.4.4
        hooks: [ {id: ruff} ]
      - repo: https://github.com/psf/black
        rev: 24.3.0
        hooks: [ {id: black} ]
    ```
    
2. **GitHub Actions** (`.github/workflows/ci.yml`)
    
    ```yaml
    name: CI
    on: [push, pull_request]
    jobs:
      build:
        runs-on: ubuntu-latest
        steps:
          - uses: actions/checkout@v4
          - uses: actions/setup-python@v5
            with: { python-version: "3.12" }
          - run: python -m pip install hatch
          - run: hatch env run pytest
    ```
    
3. **Automatic releases** with Hatch’s _version_ plugin or `git tag && gh release`.
    

* * *

## 9  Trying it out locally

```bash
git clone https://github.com/your-handle/disney-cli.git
cd disney-cli
python -m venv .venv && source .venv/bin/activate
pip install -U pip
pip install -e .[dev]   # editable + test/lint deps from [tool.hatch.envs.default]
disney hello            # ➜ Hello, world!
python -m disney hello Alice
```

* * *

## 10  Where to go next

* **Add new sub‑commands** by creating more functions in `cli.py` or splitting into modules and using `app.command()`.
    
* **Lazy‑load plugins** with Typer’s `CallbackParameter` or Click’s `Group` subclass to keep start‑up times low.
    
* **Distribute** on PyPI: `python -m build && twine upload dist/*`.
    
* **Containerise**: multi‑stage Dockerfile that installs the wheel only, or package as a single‑file **zipapp**.
    

* * *

### Recap

By combining a **src‑layout**, **Typer**, **pytest**, and a **PEP 621**‑based `pyproject.toml`, you’ve bootstrapped a **hello‑world CLI that scales**:

* It installs cleanly (`pip install disney-cli`),
    
* Runs un‑installed (`python -m disney`),
    
* Is fully testable, lintable, and CI‑ready, and
    
* Keeps the door open for plugins, sub‑commands, and production‑grade deployment.
    