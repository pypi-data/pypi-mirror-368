# Using a Python CLI Per Project Without Version Conflicts

If you’re building or using a Python-based CLI — like `obk` — you may want to **pin different versions per project**.  
This is especially useful if:

* You’re maintaining multiple projects with different CLI requirements.
    
* You want reproducible builds in CI/CD.
    
* You need to test new CLI releases without breaking existing setups.
    

In Node.js, this problem is solved by `npx`, which runs the CLI from a project’s local `node_modules`.  
In Python, we achieve the same isolation with **virtual environments**.

* * *

## 1. Why virtual environments are essential

A Python CLI like `obk` is simply a script installed into your Python environment’s `bin/` (macOS/Linux) or `Scripts\` (Windows) directory.  
Whichever directory is **first in your `PATH`** determines which version runs.

If you install `obk` globally:

```bash
pip install obk==1.2.0
pip install obk==2.0.0  # overwrites the old version
```

You can only have **one version installed at a time**, which breaks per-project workflows.

A **virtual environment** (venv) solves this by creating an isolated Python installation per project.

* * *

## 2. Per-project venv setup

The simplest approach is to keep a `.venv` folder **inside** each project:

```bash
# Create and activate venv for Project A
cd project-a
python -m venv .venv
source .venv/bin/activate     # macOS/Linux
# .\.venv\Scripts\activate    # Windows
pip install "obk==1.2.0"

# Create and activate venv for Project B
cd project-b
python -m venv .venv
source .venv/bin/activate
pip install "obk==2.0.1"
```

Each `.venv` has its own copy of `obk`:

```bash
# Project A
obk --version   # 1.2.0

# Project B
obk --version   # 2.0.1
```

When the venv is active, its `bin/` or `Scripts\` folder is **prepended to PATH**, ensuring the correct version runs.

* * *

## 3. Running without activating

You don’t have to activate the venv if you prefer not to mess with your shell session.  
You can run `obk` directly from its environment:

```bash
# macOS/Linux
./.venv/bin/python -m obk --help

# Windows
.\.venv\Scripts\python -m obk --help
```

This guarantees you’re using the version installed for that specific project.

* * *

## 4. Tool-managed environments

Instead of manually creating `.venv`, you can use a tool that **ties a venv to your project**:

| Tool | Install command | Run command |
| --- | --- | --- |
| Poetry | `poetry add --dev obk==1.2.0` | `poetry run obk` |
| Pipenv | `pipenv install --dev obk==1.2.0` | `pipenv run obk` |
| Hatch | `hatch run obk` (after adding dependency) | `hatch run obk` |
| Rye | `rye add --dev obk==1.2.0` | `rye run obk` |

These tools store the venv in a predictable location and automatically handle PATH switching for `run` commands.

* * *

## 5. One-off runs with pinned versions

For testing or CI/CD, you can run `obk` with a specific version **without** a permanent install:

```bash
# Using pipx
pipx run --spec "obk==1.2.0" obk --help

# Using uv (fast, modern installer)
uvx obk==1.2.0 --help
```

This downloads and runs the CLI in an ephemeral environment, leaving your global Python untouched.

* * *

## 6. Making it feel like `npx`

If you want `obk` to work like `npx` — automatically picking the version in the current project’s `.venv` — you can write a small launcher script that:

1. Walks up the directory tree to find a `.venv` folder.
    
2. Runs `python -m obk` from inside it.
    
3. Falls back to the global install if no venv is found.
    

Example `obk-run` script (Unix-like):

```bash
#!/usr/bin/env bash
set -e

# Find nearest .venv folder
DIR="$PWD"
while [ "$DIR" != "/" ]; do
  if [ -x "$DIR/.venv/bin/python" ]; then
    exec "$DIR/.venv/bin/python" -m obk "$@"
  fi
  DIR="$(dirname "$DIR")"
done

# Fallback to global
exec obk "$@"
```

Put this script on your PATH and `obk` will behave per-project without manual activation.

* * *

## 7. Recommendations

For most users:

* **Developers** → Create `.venv` inside the project and install `obk` there.
    
* **Teams** → Pin `obk` in `requirements.txt` or `pyproject.toml` for reproducibility.
    
* **CI/CD** → Use `pipx run` or `uvx` for explicit version control.
    

This ensures your CLI behaves **exactly like you expect** in every environment, without PATH conflicts.

* * *

If you’re the author of `obk`, documenting this per-project setup in your README will save your users a lot of frustration — and make your CLI feel as smooth as Node’s `npx`.

* * *

## Addendum  
  
Short answer: **yes** — your current packaging/entry-point setup supports per-project version pinning via venvs, and it’s easy for .NET/Node to invoke the right copy. A few small tweaks will make it rock-solid.

# Verdict

* **Works today:** Per-project venvs will each get their own `obk` launcher; `python -m obk` also works.
    
* **Cross-tech OK:** Other runtimes can call the venv’s `obk` (or `python -m obk`) by absolute path.
    
* **Minor fixes recommended:** Version reporting + dependency scoping.
    

# What already looks good

* **Console script entry point:** `[project.scripts] obk = "obk.cli:main"` → each venv gets its own `obk` shim (Windows: `.venv\Scripts\obk.exe`, Unix: `.venv/bin/obk`).
    
* **Module entry point:** `src/obk/__main__.py` → `python -m obk` works (great for explicit venv targeting).
    
* **Resource packaging:** `MANIFEST.in` + Hatch `include` cover your `xsd/` and `templates/` – good for `importlib.resources`.
    
* **Modern build:** Hatchling config + `requires-python = ">=3.9"` is clean.
    

# Gaps / quick wins

1. **Version single-source**
    
    * `pyproject.toml` shows `version = "0.9.0"` while `obk/__init__.py` has `__version__ = "0.1.0"`.
        
    * Pick one source (recommend **dynamic version** via Hatch):
        
        ```toml
        [project]
        dynamic = ["version"]
        
        [tool.hatch.version]
        path = "src/obk/__init__.py"
        ```
        
        Then keep only `__version__ = "0.9.0"` in code, or invert it and use `importlib.metadata.version("obk")`.
        
2. **`--version` flag**
    
    * Add a Typer callback or command that prints the installed dist version via:
        
        ```python
        from importlib.metadata import version
        typer.echo(version("obk"))
        ```
        
    * This helps users verify they’re hitting the expected venv-scoped version.
        
3. **Runtime vs dev dependencies**
    
    * I see `pytest`, `pluggy`, etc. in the main `[project.dependencies]`. Those should be **dev/test** only.
        
    * Move them to a Hatch env (you already have `[tool.hatch.envs.default]`) or to `[project.optional-dependencies].test`. Keep runtime deps minimal to speed installs and reduce conflicts.
        
4. **Typed consumers (optional)**
    
    * If you expect Python consumers to import `obk` as a library, ship `py.typed` and include it in the wheel so type checkers see your hints.
        

# Using obk per project (what your users can do now)

* **Venv per project**
    
    ```
    python -m venv .venv
    .\.venv\Scripts\activate   # Windows
    # or: source .venv/bin/activate
    pip install "obk==X.Y.Z"
    obk --version
    ```
    
* **No activation needed**
    
    ```
    .\.venv\Scripts\python -m obk ...   # Windows
    ./.venv/bin/python -m obk ...       # macOS/Linux
    ```
    
* **One-off runs**
    
    * `pipx run --spec "obk==X.Y.Z" obk ...` or `uvx obk==X.Y.Z ...`
        

# Cross-ecosystem invocation patterns

* **.NET (C#)**
    
    ```csharp
    var psi = new ProcessStartInfo {
        FileName = Path.Combine(projectRoot, ".venv", "Scripts", "python.exe"),
        ArgumentList = { "-m", "obk", "--help" },
        RedirectStandardOutput = true,
        UseShellExecute = false
    };
    ```
    
    (On Unix, use `.../.venv/bin/python`.)
    
* **Node.js**
    
    ```js
    const { spawn } = require("child_process");
    const py = process.platform === "win32"
      ? ".venv/Scripts/python.exe"
      : ".venv/bin/python";
    const p = spawn(py, ["-m", "obk", "--help"], { cwd: projectRoot });
    ```
    
    These patterns don’t require activation and guarantee the **project’s** `obk`.
    

# Nice-to-have (optional)

* Provide a tiny **npx-style launcher** (search up for nearest `.venv` and exec `python -m obk`) so users can just run `obk` without activating. I can draft this if you want.
    

**You:**

wouldn't I just add a toml to the .NET or nodejs root? kind of like how I use package.json in a python project just to use commitlint, even though it is a python app not node.js?

{
  "devDependencies": {
    "@commitlint/cli": "^19.8.1",
    "@commitlint/config-conventional": "^19.8.1",
    "husky": "^9.1.7"
  },
   "scripts": {
    "prepare": "husky install"
  }
}

* * *

**ChatGPT:**

Short answer: **Yes—you can drop a `pyproject.toml` in a Node.js or .NET repo purely to pin Python tooling like `obk`.** It’s the same idea as putting a `package.json` in a Python repo just to use commitlint. The TOML itself doesn’t do anything alone, though—you pair it with a Python tool runner.

Here are clean, repeatable options:

# Option A — `pyproject.toml` + `uv` (recommended)

Works great in **any** repo (Node, .NET, whatever), creates a per-repo `.venv`, and pins versions via a lockfile.

**pyproject.toml**

```toml
[project]
name = "repo-tooling"
requires-python = ">=3.10"
dependencies = ["obk==1.2.3"]  # pin your CLI version here
```

**First-time bootstrap**

```bash
uv sync          # creates .venv and installs obk==1.2.3 (writes uv.lock)
```

**Run**

```bash
uv run obk --help
```

* Add an npm script (Node repo):
    
    ```json
    {
      "scripts": {
        "postinstall": "uv sync --frozen",
        "obk": "uv run obk"
      }
    }
    ```
    
* Or a `.NET` helper script (cross-platform):
    
    * `tools/obk.sh`: `exec uv run obk "$@"`
        
    * `tools/obk.ps1`: `uv run obk $args`
        

This gives you **per-repo pinning** (via `pyproject.toml` + `uv.lock`) and no PATH headaches.

# Option B — No TOML, pin in the command with `uvx`/`pipx`

If you don’t want any Python files in the repo:

* **Node script**
    
    ```json
    {
      "scripts": {
        "obk": "uvx obk==1.2.3 -- --help"
      }
    }
    ```
    
    (Everything after `--` is passed to `obk`.)
    
* **.NET script**
    
    * `tools/obk.sh`: `exec uvx obk==1.2.3 -- "$@"`
        
    * `tools/obk.ps1`: `uvx obk==1.2.3 -- $args`
        

This pins the version **inline**. No persistent venv; `uvx` spins an ephemeral env each run (fast).

# Option C — Plain venv (no extra tooling)

Drop a `.venv` in the repo and use absolute paths:

```bash
python -m venv .venv
./.venv/bin/pip install "obk==1.2.3"
./.venv/bin/python -m obk --help    # or .venv\Scripts\python.exe -m obk on Windows
```

Add thin wrappers:

* `tools/obk.sh`: `exec ./.venv/bin/python -m obk "$@"`
    
* `tools/obk.ps1`: `./.venv/Scripts/python.exe -m obk $args`
    

* * *

## Which should you pick?

* **Want lockfile + super fast installs?** Use **Option A (uv)**.
    
* **Want zero repo files / just run it?** Use **Option B (uvx/pipx)**.
    
* **Want full control, no external runners?** Use **Option C (plain venv)**.
    

Either way, yes: a `pyproject.toml` at the root of a Node/.NET repo is a perfectly fine way to **pin `obk` per project**—just pair it with a runner (`uv`, `poetry`, etc.) and a tiny wrapper or script to call it.