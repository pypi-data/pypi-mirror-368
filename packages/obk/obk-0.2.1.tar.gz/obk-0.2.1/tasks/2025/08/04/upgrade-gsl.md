## Update OBK Repo and Validate GSL Compatibility

**Objective:**  
Sequentially implement and test all GSL compatibility and automation enhancements in the `obk` repository, as defined in the `new-gsl-elements-and-capabilities.md` article. All changes should be delivered as a single, unified change set.

---

### 1. Repository Analysis

- Analyze the `obk` repository to understand its structure and capabilities.

---

### 2. Reference Article & Feature Extraction

- Review `new-gsl-elements-and-capabilities.md` located in `articles\doing` to extract the required schema, CLI, and automation updates:
    - Add/validate support for new GSL elements and attributes in XSD
    - Update prompt examples to use all new schema features
    - Update CLI and agent logic to support and validate new conventions
    - Update CI/CD and automation for new validation and harmonization rules

---

### 3. Manual Testing & Iteration

- Review [one-line-manual-tests.md](one-line-manual-tests.md) for best practices.
- In prompt `20250804T004020+0000.md`, write single-line manual tests in `<gsl-tdd>`, each in its own `<gsl-test>` element, to cover:
    - Schema extension for new elements/attributes
    - Prompt example correctness and compatibility
    - CLI/agent validation for new schema rules
    - CI/CD enforcement and backward compatibility
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
- **Do not run, modify, or reference any file in `tasks/recurring/`. Agents must ignore all recurring tasks—only the current ad-hoc task is in scope for automated or manual work.**

**Exception:**  
- The agent may **append** to `20250804T004020+0000.md` (no edits or deletions), for traceability only.

---

**Instructions:**  
- Complete steps in order.  
- Deliver all outputs as a single, cohesive change set.

---

### Placeholders

- `<repo_name>`: `obk`
- `<reference_article>`: `new-gsl-elements-and-capabilities.md`, `obk-release-workflow.md`
- `<manual_test_guide>`: `one-line-manual-tests.md`
- `<prompt_id>`: `20250804T004020+0000`
