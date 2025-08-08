## Add XML Validation and Harmonization, as well as a command to generate a prompt id

**Objective:**  
Sequentially implement and test features in `obk` by reproducing behaviors from `prompt-validation-harmonization-guide.md`. All changes should be delivered as a single, unified change set.

---

### 1. Repository Analysis

- Analyze the `obk` repository to understand its structure and capabilities.

---

### 2. Reference Article & Feature Extraction

- Review `prompt-validation-harmonization-guide.md` and extract required CLI features or patterns (list explicitly if possible).

---

### 3. Manual Testing & Iteration

- Review `one-line-manual-tests.md` for manual test best practices (optional).
- In prompt `20250731T185109-0400.md`, write single-line manual tests in `<gsl-tdd>`, each in its own `<gsl-test>` element, covering all required behaviors and edge cases.
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
- The agent may **append** to `<prompt_id>.md` (no edits or deletions), for traceability only.

---

**Instructions:**  
- Complete steps in order.  
- Deliver all outputs as a single, cohesive change set.

---

