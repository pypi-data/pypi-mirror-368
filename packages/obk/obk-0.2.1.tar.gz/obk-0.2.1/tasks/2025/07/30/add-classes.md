## Add classes to Python project

**Objective:**  
Sequentially implement and test features in `obk` by reproducing behaviors from `articles\active\refactoring-your-python-cli-from-functions-to-classes.md`. All changes should be delivered as a single, unified change set.

---

### 1. Repository Analysis

- Analyze the `obk` repository to understand its structure and capabilities.

---

### 2. Reference Article & Feature Extraction

- Review `articles\active\refactoring-your-python-cli-from-functions-to-classes.md` and extract required CLI features or patterns (list explicitly if possible).

---

### 3. Manual Testing & Iteration

- Review `articles\active\one-line-manual-tests.md` for manual test best practices (optional).
- In prompt `20250730T062755-0400`, write single-line manual tests in `<gsl-tdd>`, each in its own `<gsl-test>` element, covering all required behaviors and edge cases.
- Iterate on implementation until all tests pass.

---

### 4. Modification Policy

**Allowed file changes:**  
- Python source: `*.py`
- Config: `pyproject.toml`, `setup.py`, `setup.cfg`, `requirements.txt`, `MANIFEST.in`
- Test config: `pytest.ini`, `tox.ini`, `.coveragerc`
- Docs: `README.md`, `.gitignore`, `.gitattributes`
- Scripts: `/scripts/*.py` or other allowed extensions

**Prohibited:**  
- Any file not listed above (e.g., arbitrary `.txt`, binary files, non-Python source, OS/user files)

**Exception:**  
- The agent may **append** to `20250730T062755-0400.md` (no edits or deletions), for traceability only.

---

**Instructions:**  
- Complete steps in order.  
- Deliver all outputs as a single, cohesive change set.

---

### Placeholders

- `obk`: repository name
- `articles\active\refactoring-your-python-cli-from-functions-to-classes.md`: article with reference behaviors
- `articles\active\one-line-manual-tests.md`: (optional) manual test design guide
- `20250730T062755-0400`: prompt file for tests

