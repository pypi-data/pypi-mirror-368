## Unit Tests Task

**Objective:**  
Sequentially implement and test features in `obk` by reproducing behaviors from the article _Bulletproof Pytest Setup_ (`articles/bullet-proof-pytest-setup.md`). All changes must be delivered in a single, unified change set.

* * *

### 1. Repository Analysis

* Analyze the `obk` repo to understand its structure and capabilities.
    

* * *

### 2. Reference Article & Feature Extraction

* Review _Bulletproof Pytest Setup_ and extract required CLI features (e.g., command help, entry point, run-from-anywhere).
    

* * *

### 3. Manual Testing & Iteration

* Review _one-line-manual-tests.md_ for manual test best practices.
    
* In prompt `20250729T185556-0400`, write single-line manual tests in `<gsl-tdd>`, each wrapped in `<gsl-test>`, covering all required behaviors and edge cases.
    
* Iterate on implementation until all tests pass.
    

* * *

### 4. Modification Policy

**Allowed file changes:**

* Python source: `*.py`
    
* Config: `pyproject.toml`, `setup.py`, `setup.cfg`, `requirements.txt`, `MANIFEST.in`
    
* Test config: `pytest.ini`, `tox.ini`, `.coveragerc`
    
* Docs: `README.md`, `.gitignore`, `.gitattributes`
    
* Scripts: `/scripts/*.py` or other allowed extensions
    

**Prohibited:**

* Any file type not listed above (e.g., arbitrary `.txt`, binary files, non-Python source, OS/user files)
    

**Exception:**

* The agent may **append** to `20250729T185556-0400.md` (no edits or deletions), for traceability only.
    

* * *

**Instructions:**

* Complete steps in order.
    
* Deliver all outputs as a single, cohesive change set.
    

* * *

### Placeholders

* `obk`: repo name
    
* `articles/bullet-proof-pytest-setup.md`: reference article
    
* `one-line-manual-tests.md`: manual test guide
    
* `20250729T185556-0400`: prompt file for tests
    

* * *