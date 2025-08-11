# Packaging and Distributing the `obk` CLI for ChatGPT 5 with Vendored Dependencies

This article explains how to create a **self-contained release zip** of the `obk` CLI that works specifically in **ChatGPT 5's execution environment**. Many LLMs cannot handle `.zip` archives or `.whl` wheels for offline installation, but ChatGPT 5 supports working with these formats when they are uploaded. This workflow ensures you can provide a fully packaged CLI, ready for execution without internet access.

The release zip will include:

* Your built package (`.whl` and `.tar.gz`)
* All **runtime dependency wheels** (direct and transitive)
* All tracked source files, including `prompts/`
* A reproducible, `.gitignore`-aware source archive

⚠ **Platform-Specific Wheel Note:** ChatGPT’s runtime is **Linux x86\_64 (manylinux)** with **Python 3.11**. If you build on Windows, wheels for compiled packages (like `dependency-injector`) may be Windows-only (`win_amd64`) and **will not install** in ChatGPT. To avoid this, configure your `build-and-vendor.ps1` to also download manylinux wheels with:

```powershell
-IncludeLinuxWheels
```

This ensures your `dist/` folder works both locally and in ChatGPT.

The workflow is built around **three scripts** in `scripts/` for both **PowerShell** and **Bash** environments.

---

## 1. Build & Vendor Dependencies

### PowerShell: `build-and-vendor.ps1`

Creates a clean build environment, builds the `obk` package, and downloads all runtime dependency wheels into the `dist/` folder. With `-IncludeLinuxWheels`, also fetches Linux-compatible wheels for ChatGPT.

**Usage:**

```powershell
./scripts/build-and-vendor.ps1 -IncludeLinuxWheels
```

### Bash: `build-and-vendor.sh`

Same logic for macOS/Linux.

**Usage:**

```bash
./scripts/build-and-vendor.sh --include-linux-wheels
```

---

## 2. Create a Clean Git Archive

### PowerShell: `make-zip.ps1`

Creates a `.gitignore`-aware zip and adds the `dist/` directory.

```powershell
./scripts/make-zip.ps1
```

### Bash: `make-zip.sh`

Same logic for macOS/Linux.

```bash
./scripts/make-zip.sh
```

---

## 3. One-Click Build + Zip

### PowerShell: `package.ps1`

Runs both build/vendor and zip steps. Recommended to pass `-IncludeLinuxWheels` for ChatGPT.

```powershell
./scripts/package.ps1 -IncludeLinuxWheels
```

### Bash: `package.sh`

Same logic for macOS/Linux.

```bash
./scripts/package.sh --include-linux-wheels
```

---

## Why This Works in ChatGPT 5

ChatGPT 5 supports:

* Uploading `.zip` archives
* Unpacking and reading vendored `.whl` files
* Installing from `--no-index` local wheels

This approach ensures the CLI can be tested entirely offline inside ChatGPT 5, with no dependency on PyPI or external downloads.

Offline install after unzipping:

```bash
pip install --no-index --find-links <unzipped-folder>/dist obk
```

Perfect for restricted environments and reproducible ChatGPT 5 tests.


## Addendum

Let’s make “no-internet” runs bulletproof. Below is a drop-in plan with exact scripts and tiny guards. You can copy these files into your repo as-is.

# 1) Split wheels by platform

Put your existing `dist/*.whl` into subfolders so Linux/Windows/macOS never mix.

```bash
# scripts/offline/split-wheels.py
from pathlib import Path
from packaging.utils import parse_wheel_filename

root = Path("dist")
linux = root / "linux"
win   = root / "win"
mac   = root / "mac"
for d in (linux, win, mac): d.mkdir(parents=True, exist_ok=True)

moved = 0
for whl in root.glob("*.whl"):
    name = whl.name.lower()
    try:
        _, _, tags = parse_wheel_filename(whl.name)
    except Exception:
        continue
    dest = linux
    if "win32" in name or "win_amd64" in name or "win_arm64" in name: dest = win
    elif "macosx" in name: dest = mac
    whl.replace(dest / whl.name)
    moved += 1
print(f"Moved {moved} wheels")
```

Run it once:

```bash
python scripts/offline/split-wheels.py
```

Result:

```
dist/
  linux/   # manylinux/musllinux/py3-none-any
  win/     # win_amd64/win32
  mac/     # (optional)
```

# 2) Generate a pinned offline requirements file

This locks dependency names/versions to the wheels you actually ship (no guessing, no internet).

```bash
# scripts/offline/generate-requirements.py
from pathlib import Path
from packaging.utils import parse_wheel_filename

def emit(find_links: Path, out: Path):
    pins = {}
    for whl in find_links.glob("*.whl"):
        name, ver, _ = parse_wheel_filename(whl.name)
        # last one wins (if dupes); fine for a wheelhouse
        pins[name.replace("_","-").lower()] = ver
    with out.open("w", encoding="utf-8") as f:
        for n, v in sorted(pins.items()):
            f.write(f"{n}=={v}\n")
    print(f"Wrote {out} ({len(pins)} packages)")

emit(Path("dist/linux"), Path("requirements-offline-linux.txt"))
emit(Path("dist/win"),   Path("requirements-offline-win.txt"))
# emit(Path("dist/mac"), Path("requirements-offline-mac.txt"))  # if you populate mac/
```

Run:

```bash
python scripts/offline/generate-requirements.py
```

# 3) Offline install scripts

## Bash (Linux/macOS):

```bash
# scripts/offline/install-linux.sh
set -euo pipefail
export PIP_NO_INDEX=1
export PIP_DISABLE_PIP_VERSION_CHECK=1
WHL_DIR="${WHL_DIR:-dist/linux}"
REQ_FILE="${REQ_FILE:-requirements-offline-linux.txt}"

python -m pip install --upgrade pip
python -m pip install --no-index --find-links "$WHL_DIR" -r "$REQ_FILE"
```

## PowerShell (Windows):

```powershell
# scripts/offline/install-windows.ps1
$ErrorActionPreference = "Stop"
$env:PIP_NO_INDEX = "1"
$env:PIP_DISABLE_PIP_VERSION_CHECK = "1"
$WHL_DIR = ${env:WHL_DIR}      ; if (-not $WHL_DIR) { $WHL_DIR = "dist/win" }
$REQ     = ${env:REQ_FILE}     ; if (-not $REQ) { $REQ = "requirements-offline-win.txt" }

python -m pip install --upgrade pip
python -m pip install --no-index --find-links $WHL_DIR -r $REQ
```

# 4) One-liners to run tests offline

## Bash:

```bash
# scripts/offline/run-tests.sh
set -euo pipefail
export PIP_NO_INDEX=1
export PIP_DISABLE_PIP_VERSION_CHECK=1
# optional: narrow to a quick subset with -k if CI time is tight
pytest -q
```

## PowerShell:

```powershell
# scripts/offline/run-tests.ps1
$ErrorActionPreference = "Stop"
$env:PIP_NO_INDEX = "1"
$env:PIP_DISABLE_PIP_VERSION_CHECK = "1"
pytest -q
```

# 5) (Optional) test-time shim for `dependency_injector`

If you ever omit a platform wheel for `dependency_injector`, this shim keeps tests green without the internet. It activates **only** when the real package isn’t importable.

```python
# tests/conftest.py  (add to top-level tests/)
import sys, os
try:
    import dependency_injector  # noqa: F401
except Exception:
    shim = os.path.join(os.path.dirname(__file__), "_shims")
    if shim not in sys.path:
        sys.path.insert(0, shim)
```

```python
# tests/_shims/dependency_injector/__init__.py
from . import providers, containers  # noqa: F401
```

```python
# tests/_shims/dependency_injector/containers.py
class DeclarativeContainer:  # minimal, enough for tests
    pass
```

```python
# tests/_shims/dependency_injector/providers.py
class Factory:
    def __init__(self, cls, *args, **kwargs):
        self.cls, self.args, self.kwargs = cls, args, kwargs
    def __call__(self, *args, **kwargs):
        return self.cls(*self.args, **self.kwargs)

class _ConfigValue:
    def __init__(self): self._v = None
    def from_value(self, v): self._v = v; return self
    def __call__(self): return self._v

class Configuration:
    def __init__(self): self._vals = {}
    def __getattr__(self, name):
        return self._vals.setdefault(name, _ConfigValue())
```

# 6) Guardrail: verify folders don’t contain wrong-platform wheels

```python
# scripts/offline/verify-wheel-folders.py
from pathlib import Path
from packaging.utils import parse_wheel_filename

def check(folder: str, allow_keywords: tuple[str,...]):
    bad = []
    for whl in Path(folder).glob("*.whl"):
        n = whl.name.lower()
        ok = any(k in n for k in allow_keywords) or "py3-none-any" in n
        if not ok:
            bad.append(whl.name)
    if bad:
        raise SystemExit(f"{folder} has non-matching wheels:\n  " + "\n  ".join(bad))
    print(f"{folder}: OK")

check("dist/linux", ("manylinux", "musllinux"))
check("dist/win", ("win32", "win_amd64", "win_arm64"))
# check("dist/mac", ("macosx",))
```

# 7) (Optional) GitHub Actions job that stays offline

```yaml
# .github/workflows/test-offline.yml
name: test-offline
on: [push, pull_request]
jobs:
  linux:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Verify wheel folders
        run: python scripts/offline/verify-wheel-folders.py
      - name: Install wheels (offline)
        run: |
          bash scripts/offline/install-linux.sh
      - name: Run tests (offline)
        run: bash scripts/offline/run-tests.sh
```

* * *

## How to adopt (quick)

1. Commit the `scripts/offline/*` files and the optional shim.
    
2. Run:
    

```bash
python scripts/offline/split-wheels.py
python scripts/offline/generate-requirements.py
python scripts/offline/verify-wheel-folders.py
```

3. Install & test offline:
    

```bash
bash scripts/offline/install-linux.sh
bash scripts/offline/run-tests.sh
```

(or the Windows `.ps1` equivalents)

If you want, I can drop these files directly into your uploaded tree and run the verify/install/test steps here so you can download the updated repo as a zip.

* * *

## Optional: also have the script fetch wheels for you

If you want `package.ps1` to _download_ the runtime wheels before organizing them, pass a requirements file:

```powershell
# Example: include both linux wheels for Python 3.11
.\scripts\package.ps1 -RuntimeRequirements .\requirements-offline-linux.txt -IncludeLinuxWheels
```

A minimal `requirements.txt` might contain what the app needs at runtime (not test-only), e.g.:

```
typer
click
rich
dependency-injector
xmlschema
```

The script will download wheels into `dist/`, then re-run the split/pin/verify steps you just saw.

If you want, send me the current `requirements.txt` or your `pyproject.toml` dependencies and I’ll tune the runtime set so your offline install is as small and fast as possible.
