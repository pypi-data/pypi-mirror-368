# Task: Harden `set-project-path` / project root resolution and add tests

## Objective

Finish the `set-project-path` feature by making it robust across OSes and Python versions, and cover it with tests.

## Scope of changes (files)

* `src/obk/cli.py`
    
* `tests/test_project_path.py` (update)
    
* `tests/test_cli.py` (minor updates if needed)
    
* _(Optional but recommended)_ `pyproject.toml` – add conditional dep for `tomli` on Python < 3.11
    

## Requirements

### 1) TOML writing: Windows paths must be valid

* When writing `project_path` to the config file, use a **TOML literal string** to avoid backslash-escape issues.
    
* Implementation in `src/obk/cli.py`, `_write_config(...)`:
    
    * For the key `project_path`, write: `project_path = '<literal-string>'`
        
    * Escape single quotes inside the path by doubling them.
        
* Example helper:
    
    ```python
    def _toml_lit(s: str) -> str:
        return "'" + s.replace("'", "''") + "'"
    ```
    
* Use `_toml_lit(str(path))` only for `project_path`.
    

### 2) `tomllib` fallback for Python < 3.11

* At top of `cli.py`, import with fallback:
    
    ```python
    try:
        import tomllib  # py311+
    except ModuleNotFoundError:  # pragma: no cover
        import tomli as tomllib
    ```
    
* _(Optional but recommended)_ Add to `pyproject.toml`:
    
    ```toml
    [project]
    dependencies = [
      # ...existing...
      "tomli>=2.0.1; python_version < '3.11'",
    ]
    ```
    

### 3) Validate project path existence

* In `resolve_project_root(*, with_source: bool=False)`:
    
    * After resolving env/config value to a `Path`, **error if it does not exist or is not a directory**:
        
        ```
        ❌ Configured project path does not exist: <path>
        ```
        
        Exit code: `1`.
        
* In `_cmd_set_project_path`:
    
    * For `--path` and `--here`, verify the directory exists (or create it if you prefer). If invalid:
        
        ```
        ❌ Not a directory: <path>
        ```
        
        Exit code: `1`.
        

### 4) Keep new resolution semantics

* No legacy “walk up” search.
    
* Default prompts dir remains `project_root / "prompts"` when `--prompts-dir` isn’t provided.
    

### 5) Minor cleanup

* Remove duplicate imports in `cli.py`.
    
* Drop `REPO_ROOT` if unused after changes.
    

## Tests (pytest)

Update/add tests to assert:

1. **Path serialization**
    
    * On a simulated Windows path (e.g., `C:\Work\obk`), run:
        
        * `obk set-project-path --path C:\Work\obk`
            
        * Assert config contains **literal TOML**: `project_path = 'C:\Work\obk'` (single quotes).
            
2. **tomllib fallback**
    
    * Monkeypatch environment to simulate Python < 3.11 only if practical. Otherwise, unit-test the import wrapper by isolating it (optional).
        
    * At minimum, ensure import fallback code path is present and not dead.
        
3. **Env vs config precedence**
    
    * Write config to `~/.config/obk/config.toml` (or `%APPDATA%\obk\config.toml` when simulating Windows), then set `OBK_PROJECT_PATH`.
        
    * `resolve_project_root()` must return env path.
        
4. **Unset error path**
    
    * Ensure neither env nor config is set.
        
    * `obk validate-all` should print:
        
        ```
        ❌ No project path configured. Run `obk set-project-path --here` or use --path <dir>.
        ```
        
        Exit code: `1`.
        
5. **Non-existent configured path**
    
    * Set config to a non-existent directory.
        
    * Any command that resolves root should error with:
        
        ```
        ❌ Configured project path does not exist: <path>
        ```
        
        Exit code: `1`.
        
6. **Happy paths**
    
    * `--here` writes the current directory to config and `--show` reports it with source `config`.
        
    * With `OBK_PROJECT_PATH` set, `validate-all` uses `<env>/prompts`.
        

> Notes for tests:

* Continue setting `PYTHONPATH` to point at `src` when invoking `python -m obk`.
    
* For Linux/macOS path behavior, use `$HOME/.config/obk/config.toml`.
    
* Add a test simulating Windows config path **only if** you keep the `%APPDATA%` fallback; otherwise, HOME-based is fine.
    

## Done when

* All above behaviors implemented.
    
* Tests added/updated and passing locally.
    
* No references remain to legacy walk-up search.
    
* CLI help text for `set-project-path` remains accurate (`--path`, `--here`, `--unset`, `--show`).
    
* Error messages exactly match specified strings (for stable automation).
    

## Nice-to-have (optional)

* If `prompts_dir` is missing under the resolved project root, print an informational note and continue (or fail—your call, just be consistent with existing behavior).
    
* Add a CHANGES/README note about the new requirement to configure project path.
    

* * *