## Add Dependency Injection with dependency-injector

**Objective:**
Sequentially implement and test dependency injection features in `obk` by reproducing behaviors from "How to Set Up Dependency Injection in Python with dependency-injector". All changes should be delivered as a single, unified change set.

---

### 1. Repository Analysis

* Analyze the `obk` repository to understand its structure and capabilities.

---

### 2. Reference Article & Feature Extraction

* Review "How to Set Up Dependency Injection in Python with dependency-injector" and extract required CLI features or patterns (list explicitly):

  * Install and configure `dependency-injector`.
  * Move core logic to service classes (e.g., `GreetingService`).
  * Create a container (`containers.py`) for dependency wiring.
  * Refactor CLI/app to use the container for dependency resolution.
  * Demonstrate configuration injection (optional).
  * Support swapping service implementations for testing (mocks).
  * Update documentation to reflect new architecture.

---

### 3. Manual Testing & Iteration

* Review the GSL prompt for single-line manual test best practices (optional).
* In prompt `20250730T104022-0400`, write single-line manual tests in `<gsl-tdd>`, each in its own `<gsl-test>` element, covering all required behaviors and edge cases.
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

**Exception:**

* The agent may **append** to `20250730T104022-0400.md` (no edits or deletions), for traceability only.

---

**Instructions:**

* Complete steps in order.
* Deliver all outputs as a single, cohesive change set.
