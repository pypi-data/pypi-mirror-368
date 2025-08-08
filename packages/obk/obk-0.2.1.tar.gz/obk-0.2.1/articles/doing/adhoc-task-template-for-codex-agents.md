# Adhoc Task Template for Codex Agents

This article provides a standardized, streamlined template for defining  ad-hoc tasks (one-off usages) for OBK/Codex agents. Use this template as a starting point for any new feature, CLI scaffold, or refactor task. Replace markers with project- or task-specific values as needed.

---

## Prompt-Driven Task Template

```markdown
## [Feature/Task]

**Objective:**  
Sequentially implement and test features in `<repo_name>` by reproducing behaviors from `<reference_article>`. All changes should be delivered as a single, unified change set.

---

### 1. Repository Analysis

- Analyze the `<repo_name>` repository to understand its structure and capabilities.

---

### 2. Reference Article & Feature Extraction

- Review `<reference_article>` and extract required CLI features or patterns (list explicitly if possible).

---

### 3. Manual Testing & Iteration

- Review `<manual_test_guide>` for manual test best practices (optional).
- In prompt `<prompt_id>`, write single-line manual tests in `<gsl-tdd>`, each in its own `<gsl-test>` element, covering all required behaviors and edge cases.
- **While writing manual tests, you may also write matching automated unit tests (e.g., pytest) if feasible, leaving these automated tests in the appropriate test locations for future use.**
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
- The agent may **append** to `<prompt_id>.md` (no edits or deletions), for traceability only.

---

**Instructions:**  
- Complete steps in order.  
- Deliver all outputs as a single, cohesive change set.

---

### Placeholders

- `<repo_name>`: repository name
- `<reference_article>`: article with reference behaviors
- `<manual_test_guide>`: (optional) manual test design guide
- `<prompt_id>`: prompt file for tests
```

---

**How to Use:**

* Copy the template block above into any new OBK/Codex prompt or task document.
* Replace each marker (e.g., `<repo_name>`, `<reference_article>`) with the actual value for your task.
* Keep instructions and modification policies clear for reliable agent execution.