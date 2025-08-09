# Automate Code Quality in Python Projects with Pre-commit, Black, Ruff, and Mypy

**Goal:**  
Keep your Python codebase clean, consistent, and error-free by automatically running code formatting, linting, and type checking every time you commit. No manual checks. No need for special commit messages.

* * *

## 1. **Why Use Pre-commit Hooks?**

* **Immediate feedback:** Errors and style violations are caught before code even leaves your computer.
    
* **Consistency:** All contributors’ code is formatted and linted the same way.
    
* **Reliability:** Type errors, linter warnings, and formatting issues don’t sneak into main.
    

* * *

## 2. **Tools Used**

* **pre-commit:** Manages and runs hooks at various git stages.
    
* **black:** Opinionated code formatter—makes code style uniform.
    
* **ruff:** Fast Python linter for catching bugs, unused code, and more.
    
* **mypy:** Static type checker for Python.
    

* * *

## 3. **Setup Steps**

### **A. Install Dependencies**

Add these to your `pyproject.toml` (dev extras), or install directly:

```bash
pip install black ruff mypy pre-commit
```

* * *

### **B. Create `.pre-commit-config.yaml`**

This file tells pre-commit what to check before every commit.

```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 24.3.0
    hooks:
      - id: black
  - repo: https://github.com/charliermarsh/ruff-pre-commit
    rev: v0.4.0
    hooks:
      - id: ruff
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.10.0
    hooks:
      - id: mypy
```

Place this at your repo root.

* * *

### **C. Install the Hooks**

```bash
pre-commit install
```

This creates a **pre-commit git hook**.  
Now, every time you run `git commit`, pre-commit will:

1. **Format your code** with black
    
2. **Lint your code** with ruff
    
3. **Type-check your code** with mypy
    

If any step fails, the commit is blocked until you fix issues.

* * *

### **D. Usage**

* Make changes, add files (`git add ...`)
    
* Try to commit:
    
    ```bash
    git commit -m "feat: add something"
    ```
    
* If your code isn’t formatted, contains linter or type errors, the commit will fail and you’ll see a message.  
    Fix the issues, re-add files, try again.
    

* * *

### **E. Example Output**

_On an unformatted file:_

```text
black....................................................................Failed
- hook id: black
- files were modified by this hook

reformatted file.py

mypy.....................................................................Passed
ruff.....................................................................Passed
```

Just re-add the reformatted file and commit.

* * *

## 4. **Optional: Run Hooks Manually**

At any time, run all hooks:

```bash
pre-commit run --all-files
```

* * *

## 5. **Summary**

With this setup:

* All code is **auto-formatted** and **linted** on every commit.
    
* **Type errors** are caught before code ever leaves your machine.
    
* You never need to remember to run tools manually—they’re automatic.
    

No enforcement of commit message style, no extra ceremony—just high code quality, always.

* * *

**Now you can develop faster, with fewer bugs and more consistent code!**