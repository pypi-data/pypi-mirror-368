## Implement Multi-XSD Prompt Validation with xmlschema and Resource Packaging

**Objective:**  
Sequentially implement and test features in `obk` by reproducing behaviors from `xsd-upgrade.md`. All changes should be delivered as a single, unified change set.

---

### 1. Repository Analysis

- Analyze the `obk` repository to understand its validation structure, prompt discovery, and current XSD handling.

---

### 2. Reference Article & Feature Extraction

- Review `xsd-upgrade.md` and extract required CLI features or patterns:
    - Multi-XSD support (mapping prompt types to schemas)
    - Schema resource loading via `importlib.resources`
    - Usage of `xmlschema` for validation
    - Error reporting and extensibility
    - CI integration for validation

---

### 3. Manual Testing & Iteration

- Review `one-line-manual-tests.md` for manual test best practices.
- In prompt `20250801T153742+0000.md`, write single-line manual tests in `<gsl-tdd>`, each in its own `<gsl-test>` element, covering all required behaviors and edge cases (including at least one valid prompt, one invalid prompt, multi-schema validation, and resource loading).
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
* **Do not run, modify, or reference any file in `tasks/recurring/`. Agents must ignore all recurring tasks—only the current ad-hoc task is in scope for automated or manual work.**


**Exception:**  
- The agent may **append** to `20250801T153742+0000.md` (no edits or deletions), for traceability only.

---

**Instructions:**  
- Complete steps in order.  
- Deliver all outputs as a single, cohesive change set.

---

### Placeholders

- `<repo_name>`: obk
- `<reference_article>`: xsd-upgrade.md
- `<manual_test_guide>`: one-line-manual-tests.md
- `<prompt_id>`: 20250801T153742+0000.md
