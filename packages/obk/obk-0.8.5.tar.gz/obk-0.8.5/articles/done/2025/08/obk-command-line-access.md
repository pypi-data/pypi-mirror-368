# Author Guide: Packaging a Python CLI to Ensure Command-Line Access After `pip install`

When publishing a Python CLI tool (like `obk`) to PyPI, it’s critical that users can type your command in their terminal after running `pip install yourpackage`—without extra steps. This article summarizes how to achieve that, the pitfalls to avoid, and best practices.

* * *

## 1. Use `console_scripts` Entry Points

The **right way** to make a CLI command available after install is to define an **entry point** in your `pyproject.toml` or `setup.py` file.

### Example for `pyproject.toml` (modern build systems):

```toml
[project.scripts]
obk = "obk.cli:main"
```

* This tells pip to install an executable named `obk` that runs `main()` from `obk/cli.py`.
    

### Example for `setup.py` (deprecated for new projects):

```python
entry_points={
    'console_scripts': [
        'obk = obk.cli:main',
    ],
},
```

* * *

## 2. Avoid Common Mistakes

* **Do not** ask users to run `python obk/cli.py` or `python -m obk.cli` unless truly necessary. This defeats the purpose of packaging a CLI!
    
* **Don’t** forget to bump the version and re-upload after any fix.
    
* **Test** in a clean virtual environment or on a fresh VM before releasing.
    

* * *

## 3. Test Your Package Like a User

After building and uploading to PyPI or TestPyPI, **always verify:**

```sh
pip install obk             # or your package name
obk --help                  # should work immediately!
```

If you want to run tests:

```sh
pytest                      # should not require the obk CLI script to be on PATH
```

* * *

## 4. The Windows PATH Problem

**On Windows**, pip installs scripts (like `obk.exe`) into a Scripts directory:

* **User install**:  
    `%USERPROFILE%\AppData\Roaming\Python\PythonXY\Scripts`
    
* **System install**:  
    `%USERPROFILE%\AppData\Local\Programs\Python\PythonXY\Scripts`
    
* Or (Microsoft Store Python):  
    `%LOCALAPPDATA%\Packages\PythonSoftwareFoundation.Python.3xx...\Scripts`
    

**If this folder is not on the user’s PATH, the command won’t be found!**

### Tips:

* **Document this in your README** so users know what to do.
    
* Instruct users to restart their terminal after installing your CLI.
    

* * *

## 5. Tips for Reducing PATH Issues

* **Encourage users to use virtual environments** (e.g., `python -m venv .venv`), which automatically put the Scripts directory on PATH when activated.
    
* **Provide a fallback:** In your README, tell users they can run `python -m obk` if all else fails.
    
* **Don’t assume** the CLI will always be immediately available, especially on Windows!
    

* * *

## 6. Troubleshooting Checklist (for Authors)

*  Are you using `[project.scripts]` or `entry_points`?
    
*  Did you bump your version number before upload?
    
*  Did you test install in a fresh virtual environment?
    
*  Did you check `obk --help` (or your command) works after install?
    
*  Did you document PATH troubleshooting for users?
    

* * *

## 7. Example: Minimal `pyproject.toml` for a CLI

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "obk"
version = "0.1.2"
dependencies = [
  "typer>=0.12",
  # ...other deps
]

[project.scripts]
obk = "obk.cli:main"
```

* * *

## 8. Further Reading

* Python Packaging User Guide: Entry Points
    
* PyPA: Packaging a Python Application
    

* * *

**Summary:**

* Use `[project.scripts]` (or `entry_points`) for CLIs
    
* Test on a clean environment
    
* Document potential PATH issues
    
* Provide `python -m yourpackage` fallback
    

* * *
