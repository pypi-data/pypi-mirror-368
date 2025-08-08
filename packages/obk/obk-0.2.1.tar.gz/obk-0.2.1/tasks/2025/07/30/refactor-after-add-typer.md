## \[Refactor Task] Finalize Typer CLI, Services, and Test Coverage

**Objective:**
Align the `services.py` module and test suite with the latest Typer-based CLI in `cli.py`, ensuring all service methods, DI patterns, and tests match the new interface.



### 1. Service Layer Audit & Upgrade

* Review `src/obk/cli.py` and identify all expected service class methods and behaviors (e.g., `Greeter.hello(name, excited)`).
* Compare with `src/obk/services.py`; add or update any missing methods, docstrings, or error handling so services match the CLI's requirements and modern best practices.



### 2. Test Suite Expansion

* Port and expand tests from Version 3 (or prior test sources), ensuring full coverage of all CLI features, including:

  * Greeter and Divider command paths.
  * Excitement flag and error handling.
  * DI overrides and mock services for all major code paths.
  * CLI exit codes and error messages.
* Add any missing tests for new CLI behaviors not covered in the current suite.



### 3. Manual Test Documentation

* In the associated prompt or specification file (`prompts/YYYY/MM/DD/...md`), update the `<gsl-tdd>` section to reflect all current features and edge cases, following the style and completeness of Version 3’s manual tests.



### 4. Clean Up

* Ensure no unused or vestigial code remains (e.g., argparse imports or dead functions).
* Run `ruff`, `black`, and `pytest` to confirm code style and test coverage.



**Allowed file changes:**

* `src/obk/services.py`
* `tests/test_cli.py`
* `prompts/`
* (any test/data/config files needed)



**Deliverable:**
A clean, Typer-first CLI project with fully updated service logic, comprehensive tests, and up-to-date manual test docs—no legacy code remaining.



### 5. General Refactoring & Quality Improvements

* Add explicit type annotations to all public methods and functions.
* Ensure all classes and methods have clear, PEP 257-compliant docstrings.
* Review custom exception classes and CLI error handling for consistency and clarity.
* Standardize CLI argument names, order, and help output for best user experience.
* Centralize configuration patterns and eliminate magic strings.
* Remove any unused imports, dependencies, or legacy files (including argparse or old test files).
* Verify CI covers linting (`ruff`), formatting (`black`), typing (`mypy`), and all tests.
* Refactor test data/fixtures for clarity and maintainability.
* (Optional) Prepare stubs for modular CLI growth if future subcommands are expected.

### Short Codex Task Template Example

> **Task:**
>
> * Update `src/obk/services.py` so all service methods and error handling match the Typer CLI interface in `src/obk/cli.py`.
> * Migrate/expand tests from Version 3 to ensure full CLI and DI coverage.
> * Clean up any obsolete code.
> * Update `<gsl-tdd>` manual tests for full scenario coverage.
