# Bulletproof Pytest Setup 

Testing is essential for professional software. Here’s how to create a **future-proof, robust, and maintainable test setup** with `pytest`—using a `src/` layout, `pyproject.toml` (no `requirements.txt`), and sensible defaults. This setup will scale from a single script to a large, multi-module project.

* * *

## 1. Project Layout

```
your-project/
│
├── src/
│   └── your_package/
│        └── __init__.py
│        └── ... (your code)
│
├── tests/
│   ├── test_example.py
│   └── conftest.py        # (shared fixtures, hooks)
│
├── pyproject.toml
├── pytest.ini
└── .gitignore, README.md, etc.
```

**Why this layout?**

* **All code in `src/`**: Prevents accidental imports from the current directory.
    
* **All tests in `tests/`**: Keeps tests and code separate—easier to manage, exclude from packages, and run CI.
    
* **`conftest.py`**: For shared pytest fixtures and hooks—scales well for bigger projects.
    

* * *

## 2. Minimal and Modern `pyproject.toml`

Specify test dependencies in the standard `[project.optional-dependencies]` section:

```toml
[project]
name = "your-project"
version = "0.1.0"
dependencies = []

[project.optional-dependencies]
test = [
    "pytest >=7.0.0",
    "pytest-cov >=4.0.0",           # test coverage reporting
    "pytest-mock >=3.10.0",         # easy mocking
    "python-dotenv >=1.0.0",        # load .env files, optional
]
```

_You can remove plugins you don’t need, but coverage and mock are highly recommended for scalable projects._

* * *

## 3. pytest.ini for Seamless Imports

```ini
[pytest]
pythonpath = src
addopts = -ra -q --cov=src --cov-report=term-missing
testpaths = tests
```

* **`pythonpath = src`**: Always finds your package, no more `PYTHONPATH` headaches.
    
* **`addopts`**:
    
    * `-ra`: Print extra info for skipped/failed tests.
        
    * `-q`: Quiet mode (less noise).
        
    * `--cov=src --cov-report=term-missing`: Coverage reporting for `src/` with line-level missing coverage shown.
        
* **`testpaths = tests`**: Only looks for tests in `tests/` (not in code).
    

* * *

## 4. Writing Robust, Scalable Tests

**In `tests/test_example.py`:**

```python
import pytest
from your_package import some_function

def test_some_function_returns_expected_value():
    assert some_function() == "expected result"

@pytest.mark.parametrize("x,expected", [
    (1, 2),
    (2, 4),
    (3, 6),
])
def test_parametrized(x, expected):
    assert your_package.double(x) == expected
```

**Shared fixtures in `tests/conftest.py`:**

```python
import pytest

@pytest.fixture
def sample_data():
    return {"foo": 1, "bar": 2}
```

Fixtures scale well—add reusable objects, database/session setup, etc.

* * *

## 5. Running Tests (with Coverage)

**From the project root:**

```sh
pytest
```

or, for just coverage:

```sh
pytest --cov=src --cov-report=term-missing
```

* Output will show missing lines, so you know what to add tests for.
    

* * *

## 6. Version Control and CI

* **Ignore cache files:** Add `.pytest_cache/` and `.coverage` to `.gitignore`.
    
* **CI:**
    
    * Use `pytest` with coverage flags in your workflow.
        
    * Artifacts (e.g., HTML reports) can be generated via `--cov-report=html`.
        

* * *

## 7. Optional: Loading `.env` Automatically

Add a `.env` file (for secrets or env vars).  
`pytest` will load it if you have [`python-dotenv`](https://github.com/theskumar/python-dotenv) installed and add `--dotenv=.env` to your addopts.

* * *

## 8. Checklist for Robust, Maintainable Pytest Setup

*  **All code in `src/`**
    
*  **All tests in `tests/`**
    
*  **Test dependencies only in `pyproject.toml`**
    
*  **No `requirements.txt`**
    
*  **`pytest.ini` ensures smooth imports and coverage**
    
*  **Add plugins: `pytest-cov`, `pytest-mock`**
    
*  **Use fixtures and parameterized tests for scalability**
    
*  **CI uses `pytest` with coverage flags**
    

* * *

## 9. Example Files (Copy-Paste Ready)

**`pyproject.toml`**

```toml
[project]
name = "your-project"
version = "0.1.0"
dependencies = []

[project.optional-dependencies]
test = [
    "pytest >=7.0.0",
    "pytest-cov >=4.0.0",
    "pytest-mock >=3.10.0",
]
```

**`pytest.ini`**

```ini
[pytest]
pythonpath = src
addopts = -ra -q --cov=src --cov-report=term-missing
testpaths = tests
```

**`tests/conftest.py`**

```python
import pytest

@pytest.fixture
def sample_data():
    return {"foo": 1, "bar": 2}
```

* * *

## 10. Conclusion

This configuration gives you:

* Fast startup for new tests
    
* Scalable structure for big projects
    
* Automatic coverage reporting
    
* Easy fixtures and mocks
    
* Minimal setup steps (no more manual PYTHONPATH)
    
* Fully modern Python packaging workflow
    

* * *