# How to Publish obk to PyPI

This guide walks you through publishing your `obk` project—a modern, scalable hello-world CLI starter—using the standard Python packaging toolchain.

---

## 1. Prepare Your Project Structure

Assuming your repository is named `obk` and uses the modern **src layout**:

```
.
├── pyproject.toml
├── README.md
├── LICENSE
├── src/
│   └── obk/
│       ├── __init__.py
│       └── ... (modules)
└── tests/
    └── ...
```

* The **package** lives under `src/obk/`, importable as `import obk`.
* The **repo root** is the top-level directory (shown as `.` above).

---

## 2. Create `pyproject.toml`

All build and metadata live here. A simplified version for `obk`:

```toml
[build-system]
requires = ["hatchling>=1.24"]
build-backend = "hatchling.build"

[project]
name = "obk"
version = "0.1.0"
description = "A scalable hello-world CLI starter. This is a pre-release/alpha version for initial feedback and CI testing. Not for production use."
readme = "README.md"
requires-python = ">=3.9"
authors = [{ email = "hello@evenflow.dev" }]
dependencies = [
    "typer>=0.12",
    "dependency-injector>=4.41",
]

[project.scripts]
obk = "obk.cli:main"

[tool.hatch.build.targets.wheel]
packages = ["src/obk"]
```

*Adjust the author and metadata as needed.*

---

## 3. Build Your Package

Use [Hatch](https://hatch.pypa.io/) to build:

```bash
python -m pip install --upgrade hatch
hatch build
```

This creates a `dist/` directory with `.tar.gz` and `.whl` files.

---

## 4. Register and Set Up PyPI Account

* [Register on PyPI](https://pypi.org/account/register/)
* Verify your email.
* *(Optional but recommended)*: Enable two-factor authentication.
* [Create an API token](https://pypi.org/manage/account/#api-tokens) for uploading (prefer over passwords).

---

## 5. Install Twine

Install [Twine](https://twine.readthedocs.io/):

```bash
python -m pip install --upgrade twine
```

---

## 6. Upload Your Package

**Note:** If you haven’t already built your package, run:

```bash
hatch build
```

This will create the `dist/` directory needed for uploading.

Upload your package (using your API token):

```bash
python -m twine upload dist/*
```

You’ll be prompted for credentials. Use `__token__` as the username and paste your API token as the password.

---

## 7. Verify Your Package

* Visit [`https://pypi.org/project/obk/`](https://pypi.org/project/obk/).
* Try installing it in a fresh environment:

  ```bash
  pip install obk
  obk --help
  ```

---

## 8. Tips and Best Practices

* **Choose a unique name:** Check availability at `https://pypi.org/project/<your-package-name>/`.
* **Import name vs. distribution name:** Use underscores for your Python import (`obk`), hyphens for the PyPI package (`obk` or `obk-cli`).
* **Include a license and clear README.**
* **Bump the version** for every release.
* **Always test locally** before uploading:

  ```bash
  pip install dist/obk-0.1.0-py3-none-any.whl
  ```

---

## 9. Optional: Test Uploads to TestPyPI

To avoid polluting the main index:

```bash
python -m twine upload --repository testpypi dist/*
pip install --index-url https://test.pypi.org/simple/ obk
```

---

## 10. Useful Resources

* [Packaging Python Projects — Official Guide](https://packaging.python.org/en/latest/tutorials/packaging-projects/)
* [PyPI — Managing Projects](https://pypi.org/help/)
* [Hatchling documentation](https://hatch.pypa.io/latest/)

---

## How to Test These Instructions

* Build the package: `hatch build`
* Upload to TestPyPI: `python -m twine upload --repository testpypi dist/*`
* Install and verify in a fresh environment: `pip install --index-url https://test.pypi.org/simple/ obk`
* Run: `obk --help`

## What to Do When Things Go Wrong

### Common Problems and How to Respond

**1. The wrong README or description is published**

* You cannot change files or metadata for an already-published version on PyPI.
    
* **Solution:** Update your `README.md` and description in `pyproject.toml`, bump the version number, rebuild, and publish a new version. Only the new release will reflect the fix.
    

**2. You want to discourage downloads of a published version (e.g., alpha, test, broken)**

* **Yank the release** on PyPI. This marks it as unavailable for normal installs, but it remains visible on the project page.
    
    * Via command line:
        
        ```bash
        twine yank obk-0.1.0-py3-none-any.whl
        ```
        
    * Or via the PyPI web UI: Go to the release page and click “Yank”.
        
* Add a warning banner to your `README.md` (top of file):
    
    ```markdown
    > **WARNING:** This version is for testing only. Do not use in production.
    ```
    
* You may also update the project description in your next release for clarity.
    

**3. Can you delete a release?**

* You can delete release files for a specific version from PyPI (web UI > Manage files > Delete).
    
* **Important:** You cannot re-upload that version number again—it's permanently reserved.
    
* You can always publish a new version (`0.1.1`, etc.).
    

**4. You want to publish a corrected release after a mistake**

* Update your code and/or metadata, bump the version in `pyproject.toml`, rebuild (`hatch build`), and upload as a new version.
    
* Make sure `README.md` and all metadata are correct before building and uploading.
    

**5. PyPI rejects your upload**

* Typical reasons: duplicate version, metadata error, missing files, or account permission problem.
    
* Read the error message carefully and address the issue before retrying.
    

**6. Your package name is taken**

* PyPI names are global and permanent. You must pick a new, unique name.
    

**7. How do I communicate that a version is deprecated or not for use?**

* Use yanking, warning banners, and clear descriptions in both your `README.md` and the PyPI project description for future releases.
    

### General Advice

* Double-check all files (especially `README.md`) before building and uploading.
    
* Treat every PyPI publish as permanent for that version.
    
* Consider experimenting with [TestPyPI](https://test.pypi.org/) first.
    

* * *
