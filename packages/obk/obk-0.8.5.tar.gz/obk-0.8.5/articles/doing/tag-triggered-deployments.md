# **Implementing Tag-Creation–Triggered Deployments with GitHub Actions**

* * *

## **Overview**

This guide describes how to build a modern, robust Python deployment workflow where **releases are triggered exclusively by creating a Git tag** (e.g., `v1.2.3`). It assumes you are starting from a minimal CI setup that only runs tests and builds on pushes to `main`, and walks you through evolving it into a version-safe, tag-triggered deploy system.

* * *

## **Motivation**

* **Prevent accidental releases**: Deployments only happen when you explicitly create a tag.
    
* **Guarantee reproducibility**: The version in `pyproject.toml` must always match the released tag.
    
* **Keep automation simple**: No more ambiguous commit-message deploy triggers, manual version bumps after deploy, or complex branching strategies.
    
* **Enable safe, auditable releases**: Every deploy has a clear, single source of truth.
    

* * *

## **Step 1: Prepare Your Minimal CI Skeleton**

Your starting `ci-cd.yml` should look like:

```yaml
name: CI-CD Pipeline

on:
  push:
    branches: main

permissions:
  contents: write

jobs:
  test:
    runs-on: self-hosted
    steps:
      - uses: actions/checkout@v4
      - name: Clean workspace
        run: git clean -fdx
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Run tests
        run: |
          python3 -m venv .venv
          .venv/bin/pip install --upgrade pip
          .venv/bin/pip install -e .[test]
          .venv/bin/pytest -q

  build:
    needs: test
    runs-on: self-hosted
    steps:
      - uses: actions/checkout@v4
      - name: Build package
        run: |
          python3 -m venv .venv
          .venv/bin/pip install build
          .venv/bin/python -m build
```

* * *

## **Step 2: Enable Tag-Based Workflow Triggers**

Expand your workflow to respond to both `push` to `main` (for CI) and to version tags for deployments.

```yaml
on:
  push:
    branches: main
    tags:
      - 'v*.*.*'
```

* * *

## **Step 3: Add a Tag-Triggered Deploy Job**

Add a `deploy` job that:

* Depends on `build`
    
* Only runs for tag pushes that look like version releases
    
* Will validate version before deploying
    

Example skeleton:

```yaml
deploy:
  needs: build
  if: startsWith(github.ref, 'refs/tags/v')
  runs-on: self-hosted
  steps:
    - uses: actions/checkout@v4
    - name: Placeholder
      run: echo "Ready to deploy on tag"
```

* * *

## **Step 4: Validate `pyproject.toml` Version Matches Tag**

Before you build and deploy, ensure the version in `pyproject.toml` matches the tag. Add this as the **first real step** in your `deploy` job:

```yaml
- name: Validate pyproject.toml version matches tag
  run: |
    TAG_VERSION="${GITHUB_REF##*/}"
    PY_VERSION=$(python3 -c "import toml; print(toml.load(open('pyproject.toml'))['project']['version'])")
    if [ "v$PY_VERSION" != "$TAG_VERSION" ]; then
      echo "Version mismatch: pyproject.toml ($PY_VERSION) != tag (${TAG_VERSION#v})"
      exit 1
    fi
```

> **Tip:** You’ll need to ensure the `toml` module is available (add `python3 -m pip install toml` before this step if it’s not already).

* * *

## **Step 5: Build and Upload to PyPI**

Add the following steps (after validation) to package and deploy to PyPI:

```yaml
- name: Set up Python
  uses: actions/setup-python@v5
  with:
    python-version: '3.11'

- name: Install dependencies
  run: python3 -m pip install --upgrade pip build twine

- name: Build package
  run: python3 -m build

- name: Upload to PyPI
  env:
    TWINE_USERNAME: __token__
    TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
  run: python3 -m twine upload dist/*
```

* * *

## **Full Example: Final Workflow Snippet**

```yaml
deploy:
  needs: build
  if: startsWith(github.ref, 'refs/tags/v')
  runs-on: self-hosted
  steps:
    - uses: actions/checkout@v4

    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: '3.11'

    - name: Install dependencies
      run: python3 -m pip install --upgrade pip toml build twine

    - name: Validate pyproject.toml version matches tag
      run: |
        TAG_VERSION="${GITHUB_REF##*/}"
        PY_VERSION=$(python3 -c "import toml; print(toml.load(open('pyproject.toml'))['project']['version'])")
        if [ "v$PY_VERSION" != "$TAG_VERSION" ]; then
          echo "Version mismatch: pyproject.toml ($PY_VERSION) != tag (${TAG_VERSION#v})"
          exit 1
        fi

    - name: Build package
      run: python3 -m build

    - name: Upload to PyPI
      env:
        TWINE_USERNAME: __token__
        TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
      run: python3 -m twine upload dist/*
```

* * *

## **Release Workflow (User’s Perspective)**

1. Make and merge feature branches to `main` as needed.
    
2. When ready to release:
    
    * Bump the version in `pyproject.toml` and merge to `main`.
        
    * Create a tag (e.g., `v1.2.3`) **matching** the new version.
        
3. The workflow:
    
    * Runs tests and build as usual.
        
    * When triggered by the tag, validates the version.
        
    * Deploys to PyPI **only if the tag matches the version**.
        

* * *

## **Best Practices and Tips**

* **Never deploy from a commit-message trigger or untagged commit.**
    
* **Do not bump the version after tagging:** always do it before creating the tag.
    
* **Keep `main` as your only long-lived branch for releases.**
    
* **Protect your `main` branch:** require PRs and successful CI before merging.
    

* * *

## **Troubleshooting**

* If deployment fails with a “version mismatch,” check:
    
    * Did you forget to bump `pyproject.toml`?
        
    * Does the tag name match the version format (`v1.2.3`)?
        
* If PyPI upload fails, verify your `PYPI_API_TOKEN` secret.
    

* * *

## **Summary**

By shifting to a tag-triggered deploy workflow, you:

* Eliminate ambiguous or risky deploy logic.
    
* Make every release auditable and intentional.
    
* Keep your project simple, reproducible, and modern.
    

* * *

If you need to adapt this for another language or packaging tool, swap the `build`/`twine` commands for the relevant alternatives.

* * *

**End of Article**