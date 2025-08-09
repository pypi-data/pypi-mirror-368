## [Maintenance Task] Code Lint and Dependency Cleanup

**Objective:**  
Clean up the codebase for `obk` by applying routine maintenance, addressing lint/formatting warnings, and removing unused dependencies or files as needed.

* * *

### Steps

1. **Linting and Formatting**
    
    * **Install `ruff` and `black` if not already installed:**
        
        ```bash
        pip install ruff black
        ```
        
    * Run `ruff` on the entire codebase and fix all warnings (unused imports, variables, etc.).
        
    * Run `black` to auto-format all Python files.
        
    * Verify both tools report zero issues.
        
2. **Dependency Cleanup**
    
    * Remove any dependencies from `pyproject.toml` or `requirements.txt` not used in the codebase (e.g., `typer[all]` if Typer is unused).
        
    * Update lock files as needed _only if_ dependencies change (`poetry lock`, `pip-compile`).
        
3. **Test Hygiene**
    
    * Ensure that `pytest-cov` and `dependency-injector` are present in development dependencies if required for running tests.
        
    * Run all tests to confirm nothing is broken and coverage is maintained.
        
4. **Remove Dead Code**
    
    * Delete or refactor any unused imports, functions, or files as identified by linting or analysis.
        

* * *

### Allowed file changes

* Python source: `*.py`
    
* Dependency/config files: `pyproject.toml`, `requirements.txt`
    
* Lock files: `poetry.lock`, `Pipfile.lock`
    
* Test config: `pytest.ini`, `.coveragerc`
    
* Lint/format config: `.ruff.toml`, `pyproject.toml` (for black and ruff)
    
* No other files may be changed unless strictly required for fixes above.
    

* * *

**Instructions:**

* Complete all steps in order.
    
* Commit all changes together.
    
* Ensure the codebase passes all linter, formatter, and test checks locally and in CI with zero errors or warnings.
    
* **No functional/code logic changes are permitted unless strictly required for compliance.**
    

* * *