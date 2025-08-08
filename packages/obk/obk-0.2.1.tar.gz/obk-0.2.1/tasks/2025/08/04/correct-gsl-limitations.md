
## Correcting GSL Implementation Limitations

**Objective:**  
Address and resolve the limitations of the current GSL schema and validation logic in the `obk` repository by implementing improvements described in `gsl-implementation-limitations.md`. All changes should be delivered as a single, cohesive change set, with reproducible manual and automated tests.

* * *

### 1. Repository Analysis

* Analyze the `obk` repository to understand existing GSL schema (`prompt.xsd`), Python validation logic, and related CLI/test infrastructure.
    

* * *

### 2. Reference Article & Limitation Extraction

* Review `gsl-implementation-limitations.md` and extract each documented limitation and corresponding recommended mitigation.
    

* * *

### 3. Manual and Automated Testing

* Consult `one-line-manual-tests.md` for guidance on writing manual tests.
    
* In prompt `20250804T014131+0000.md`, add new `<gsl-test>` elements under `<gsl-tdd>` for each corrected limitation, following the one-line/manual test convention.
    
* Where possible, **also add or generate matching automated unit tests** for any new or changed behavior, leaving these for maintainers or future automation.
    
* Iterate until all manual tests pass and new/modified automated tests are stable.
    

* * *

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

* The agent may **append** to `20250804T014131+0000.md` (no edits or deletions), for traceability only.
    

* * *

**Instructions:**

* Complete steps in order.
    
* Deliver all outputs as a single, cohesive change set.
    

* * *

### Placeholders

* `<repo_name>`: obk
    
* `<reference_article>`: gsl-implementation-limitations.md
    
* `<manual_test_guide>`: one-line-manual-tests.md
    
* `<prompt_id>`: 20250804T014131+0000
    

* * *