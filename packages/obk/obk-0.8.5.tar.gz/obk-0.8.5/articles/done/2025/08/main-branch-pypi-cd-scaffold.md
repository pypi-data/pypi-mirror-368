# main-branch-pypi-cd-scaffold.md

> **Purpose:**  
> This guide documents the pre-release deployment pipeline for the OBK project, using a single self-hosted runner and automated publishing to PyPI from the `main` branch.
> 
> **Pre-1.0.0 Policy:**  
> Before version 1.0.0, **anything goes**: we may bump minor or patch versions arbitrarily, and breaking changes or workflow adjustments are expected as features stabilize. The emphasis is on iteration and rapid feedback, not on strict versioning or API stability.
> 
> This is not a minimal or “final” production pipeline, but rather a fast-moving scaffold tailored to the needs of early development and pre-release publishing.  
> A separate article will document our post-1.0.0, stable-release workflow.

* * *

## 1. Branching & Protection

* **Main branch as deployment branch:**
    
    * All deploys are performed from the permanent `main` branch.
        
    * Protect `main`: PRs only, review required, status checks enabled, no force push or direct push.
        
    * Feature work is done on `feature/*` branches and merged to `main` via PR.
        
    * Once merged to `main`, the **deploy** workflow runs; PyPI deployment only occurs if `[deploy]` is present in the squash-merge commit message.
        

* * *

## 2. Single Self-Hosted Runner

* Use one self-hosted runner for both CI and CD tasks.
    
* Make sure this runner is secure and updated, but it can be general-purpose.
    

* * *

## 3. Automatic Patch Version Bump

> **Why:**  
> PyPI will reject uploads if the version hasn’t changed.  
> We bump the Z (patch) version in `pyproject.toml` before every **deploy** to ensure every upload is unique.

* **Add this script to your repo:** `.github/scripts/bump_patch.py`
    

```python
# .github/scripts/bump_patch.py
import re
from pathlib import Path

pyproject = Path("pyproject.toml")
content = pyproject.read_text(encoding="utf-8")

match = re.search(r'version\s*=\s*"(\d+)\.(\d+)\.(\d+)"', content)
if not match:
    raise SystemExit("Could not find version string in pyproject.toml!")

major, minor, patch = map(int, match.groups())
patch += 1

new_version = f'{major}.{minor}.{patch}'
new_content = re.sub(
    r'version\s*=\s*"\d+\.\d+\.\d+"',
    f'version = "{new_version}"',
    content
)

pyproject.write_text(new_content, encoding="utf-8")
print(f"Bumped version to {new_version}")
```

* * *

## 4. CI/CD Combined Workflow (`ci-cd.yml`)

* **Workflow file:** `.github/workflows/ci-cd.yml`
    
* **Trigger:** Push to `main` branch
    
* **Enforces Test-before-Deploy**
    

    ```yaml
    name: CI-CD Pipeline
    
    on:
      push:
        branches: main
    
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
        if: success()
        runs-on: self-hosted
    
        steps:
          - uses: actions/checkout@v4
          - name: Build package
            run: |
              python3 -m venv .venv
              .venv/bin/pip install build
              .venv/bin/python -m build
    
      deploy:
        needs: build
        if: >
          success() &&
          contains(github.event.head_commit.message, '[deploy]')
        runs-on: self-hosted
        steps:
          - uses: actions/checkout@v4
          - name: Set up venv, bump version, and deploy
            run: |
              python3 -m venv .venv
              .venv/bin/pip install --upgrade pip build twine
              .venv/bin/python .github/scripts/bump_patch.py
              .venv/bin/python -m build
              .venv/bin/twine upload dist/*
            env:
              TWINE_USERNAME: __token__
              TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
    ```

    > **Notes:**  
    > - The `needs:` keyword and `if: success()` conditions prevent further steps from executing if a previous job fails.
    > 
    > - Deployments **only** occur if `[deploy]` is present in the latest commit message on `main` (typically your squash-merge commit message).  
    > Otherwise, only tests and build run—no PyPI publish.
    >
    > **Enabling Required Status Checks (Highly Recommended):**
    > 
    > After you have committed and merged your `.github/workflows/ci-cd.yml` file to `main` and have run at least one successful pipeline,  
    > **enable required status checks** for your `main` branch:
    > 
    > 1. Go to **Settings → Branches** in your GitHub repository.
    >     
    > 2. Under “Branch protection rules,” create or edit a rule for `main`.
    >     
    > 3. Add the following required status checks:
    >     
    >     * `test` (or the exact name of your “test” job)
    >         
    >     * `build` (optional, if you want to block on a passing build)
    >         
    >     * `deploy` (optional, for deploy-required PRs)
    >         
    > 4. Enable “Require status checks to pass before merging.”
    >     
    > 5. Save the branch protection rule.
    >     
    > 
    > This will **prevent PRs from being merged** until all required jobs in your CI/CD pipeline have succeeded.
    > 
    > _Note: You will only see jobs in the status check list after the workflow has run at least once on `main`. If a job isn’t listed, trigger a run by pushing a commit to `main` and refresh the settings page._



* * *

## 5. Deployment Maintenance Workflow

After each successful deployment to PyPI, the version in your `pyproject.toml` will be bumped on the runner’s workspace, but this change will **not** be committed back to the repository automatically.

Perform maintenance steps after each release:

1. Create a branch: `ci/update-version-YYYYMMDD`
    
2. Update `pyproject.toml` version manually.
    
3. Commit, push, open PR, and merge into `main`.
    

* * *

## 6. Step-by-Step Setup Workflow

Follow these steps to configure your OBK pre-release deployment pipeline:

**6.1. Set Up Branching and Protection (see Section 1)**

* Ensure your `main` branch is protected:
    
    * Require PRs, approvals, status checks.
        
    * Disallow direct pushes and force pushes.
        

**6.2. Set Up Single Self-Hosted Runner (see Section 2)**

* Register and configure a self-hosted GitHub runner.
    
* Label it appropriately (e.g., `self-hosted`).
    

**6.3. Configure PyPI Credentials**

* Generate PyPI API token ([PyPI token setup](https://pypi.org/help/#apitoken)).
    
* Add this as `PYPI_API_TOKEN` in GitHub repo secrets.
    

**6.4. Add Patch Version Bump Script (see Section 3)**

* Save the provided script (`bump_patch.py`) to `.github/scripts/`.
    
* Commit and push.
    

**6.5. Create Combined CI/CD Workflow (see Section 4)**

* Create `.github/workflows/ci-cd.yml`.
    
* Copy the CI/CD YAML provided in Section 4.
    
* Ensure jobs (`test`, `build`, `deploy`) are sequenced properly.
    

**6.6. Create Release-Drafter Workflow**

* Set up Release Drafter in `.github/workflows/release-drafter.yml`.
    
* See [release-drafter.yml](.github/workflows/release-drafter.yml) for details.
    
* This ensures changelog automation upon GitHub Release publishing.
    

**6.7. Set Up PR Deployment Checklist (see Section 9.1)**

* Create `.github/pull_request_template.md`.
    
* Use the provided PR checklist for explicit deployment control.
    

**6.8. Test Your Workflow**

* Open a trivial feature branch, then PR into `main`.
    
* Use PR checklist to confirm deployment or non-deployment PR.
    
* Merge PR and ensure:
    
    * Tests run first (and fail properly stops the pipeline).
        
    * Version bumps automatically.
        
    * Package is published to PyPI (confirm on [PyPI](https://pypi.org/)) only if `[deploy]` was present in the squash-merge commit message.
        

**6.9. Codex Automation Setup (optional, see Section 9.2)**

* After a successful GitHub Release:
    
    * Manually run Codex task on a dedicated branch.
        
    * Review, merge as a non-deployment commit.
        

**6.10. Regular Deployment Maintenance (see Section 5)**

* After each deploy, manually sync version in `pyproject.toml`.
    

**6.11. Update `ci-cd.yml` for Deploy-on-Commit-Message**

> * Ensure the `deploy` job in `.github/workflows/ci-cd.yml` is guarded by:  
>     `if: > success() && contains(github.event.head_commit.message, '[deploy]')`
>     
> * This ensures deployment **only** happens for squash-merge commits with `[deploy]` (see Section 9.5).
>  
    
* This ensures deployments only occur when `[deploy]` is present in your squash-merge commit message (see Section 9.5).



    

* * *

## 7. Optional Next Steps

* Add version bump automation for setup files.
    
* PR template for releases.
    
* Gradually introduce more automated changelog management.
    

* * *

## 8. References

* [ci.yml](.github/workflows/ci.yml)
    
* [commitlint.yml](.github/workflows/commitlint.yml)
    
* [release-drafter.yml](.github/workflows/release-drafter.yml)
    
* [PyPI token setup](https://pypi.org/help/#apitoken)
    
* GitHub self-hosted runners
    

* * *

## 9. Other Workflows

#### 9.1. Manual PR Checklist for Deployment Control

To explicitly manage deployment vs. non-deployment PRs, use this PR checklist (`.github/pull_request_template.md`):

```markdown
### PR Deployment Checklist

- [ ] This PR is a deployment PR (intended to publish to PyPI)
    - If checked, I will add **[deploy]** to the **squash commit message** when merging to `main`.
- [ ] This PR is a non-deployment PR (docs, chores, automation only)
- [ ] Changelog updated (Codex automation task run after GitHub Release)
```

**Instructions:**

* If you want this PR to trigger a PyPI deployment, check the first box and ensure you include `[deploy]` in the final squash-merge commit message.
    
* If not, leave `[deploy]` out—the **deploy** job will be skipped. Checking the box does not trigger deployment on its own; `[deploy]` must appear in the squash-merge commit message.

#### 9.2. Codex Automation: README + CHANGELOG Maintenance

* After publishing a GitHub Release (via Release Drafter), manually run Codex tasks:
    
    1. Create branch `codex-automation`.
        
    2. Trigger Codex recurring tasks for `README.md` and `CHANGELOG.md`.
        
    3. Review changes, commit, and open a PR.
        
    4. Merge to `main` as a non-deployment commit.
        

#### 9.3. GitHub Release & Changelog

* Create and publish GitHub Releases manually.
    
* Changelog updated automatically by Release Drafter upon publishing.
    

#### 9.4. Avoiding Deploy Loops & Protecting `main`

* Deployments only occur explicitly through PRs to protected `main`.
    
* Mistakes or accidental pushes require manual intervention and correction.
    

* * *

#### 🚩 9.5. Deploy-on-Commit-Message Strategy (Pre-Release & Post-1.0.0 Note)

> **Goal:** Deployments only occur when `[deploy]` appears in the commit message for a merge to `main`.

##### **How Does Deployment Trigger Work?**

* To trigger deployment, simply include `[deploy]` anywhere in your **squash-merge commit message** when merging a PR into `main`.
    
* If `[deploy]` is **absent** from the commit message, the **deploy** job will **not run**—even if merged to main.
    
* There is **no need** to add GitHub labels or check PR boxes. All control is via the commit message!
    

**Example:**

```
feat: add fuzzy search option [deploy]

- CLI: `obk search --fuzzy`
- Docs: add fuzzy usage to README

[deploy]
```

##### **How it works:**

1. When you squash-merge a PR, include `[deploy]` in the message to deploy.
    
2. If `[deploy]` is not present, CI runs but PyPI deployment is skipped.
    
3. This gives you fine-grained control—deploy _only when you mean to_.
    

* * *

##### **Post-1.0.0 (stable):**

* After 1.0.0, you may adopt conventions like `[major]`, `[minor]`, `[patch]` in commit messages to automate version bumping and stricter release workflows.
    
* For now (pre-release), **anything goes**—just control deploys via `[deploy]` in commit messages.
    

* * *

##### **Workflow: ci-cd.yml (Deploy Job Conditional on Commit Message)**

Replace your current `deploy` job with:

```yaml
deploy:
  needs: build
  if: >
    success() &&
    contains(github.event.head_commit.message, '[deploy]')
  runs-on: self-hosted

  steps:
    - uses: actions/checkout@v4
    - name: Set up venv, bump version, and deploy
      run: |
        python -m venv .venv
        .venv/bin/pip install --upgrade pip build twine
        .venv/bin/python .github/scripts/bump_patch.py
        .venv/bin/python -m build
        .venv/bin/twine upload dist/*
      env:
        TWINE_USERNAME: __token__
        TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
```

> **Note:**  
> This requires that `[deploy]` appears in the latest commit message on `main` (typically your PR’s squash-merge commit). If not present, no **deploy** occurs.



**Result:**  
You can squash-merge any PR—but **only those with `[deploy]` in the commit message will deploy**.


* * *

## 10. Final Recommendations & Considerations

* **Explicit Workflow**: All deploy-related tasks require manual PR approval and review.
    
* **Branch Protection**: Protecting `main` branch prevents unintended deployments.
    
* **Failure Control**: Jobs in one YAML file ensure tests always run before deploy; failures stop subsequent jobs automatically.
    
* **Single Runner**: Acceptable for early development; revisit later if needed for reliability.
    

* * *