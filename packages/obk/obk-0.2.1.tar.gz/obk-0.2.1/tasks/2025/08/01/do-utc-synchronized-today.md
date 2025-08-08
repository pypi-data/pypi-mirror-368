## UTC-Synchronized “Today” Folder Logic for obk

**Objective:**
Sequentially implement and test UTC-synchronized “today” folder logic in the `obk` repository by reproducing behaviors from `utc-synchronized-today-logic.md`. All changes should be delivered as a single, unified change set.

---

### 1. Repository Analysis

* Analyze the `obk` repository to understand its structure and capabilities.

---

### 2. Reference Article & Feature Extraction

* Review `utc-synchronized-today-logic.md` and extract required CLI features or patterns:

  * Refactor all “today”-dependent commands (including `trace-id`, `validate-today`, `harmonize-today`) to use a unified UTC-synchronized folder/date logic by default, with explicit timezone override support.
  * Add or update a `--timezone` CLI flag for each command, defaulting to `UTC`, and update CLI help output to document this option.
  * Ensure all commands reference the same folder for “today” under all scenarios, including user timezone overrides.

---

### 3. Manual Testing & Iteration

* Review `one-line-manual-tests.md` for manual test best practices.
* In prompt `20250802T024329+0000`, write single-line manual tests in `<gsl-tdd>`, each in its own `<gsl-test>` element, covering all required behaviors and edge cases.
* Iterate on implementation until all tests pass.

---

### 4. Modification Policy

**Allowed file changes:**

* Python source: `*.py`
* Config: `pyproject.toml`, `setup.py`, `setup.cfg`, `requirements.txt`, `MANIFEST.in`
* Test config: `pytest.ini`, `tox.ini`, `.coveragerc`
* Docs: `README.md`, `.gitignore`, `.gitattributes`
* Scripts: `/scripts/*.py` or other allowed extensions

**Prohibited:**

* Any file not listed above (e.g., arbitrary `.txt`, binary files, non-Python source, OS/user files)
* **Do not run, modify, or reference any file in `tasks/recurring/`. Agents must ignore all recurring tasks—only the current ad-hoc task is in scope for automated or manual work.**

**Exception:**

* The agent may **append** to `20250802T024329+0000.md` (no edits or deletions), for traceability only.

---

**Instructions:**

* Complete steps in order.
* Deliver all outputs as a single, cohesive change set.

---

### Placeholders

* `obk`: repository name
* `utc-synchronized-today-logic.md`: article with reference behaviors
* `one-line-manual-tests.md`: manual test design guide
* `20250802T024329+0000`: prompt file for tests
