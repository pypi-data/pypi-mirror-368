## How to Automate Updating `pyproject.toml` Version After Release (with GitHub Actions, No Extra Tools)

Keeping the version in your `pyproject.toml` in sync with your latest release is essential for reproducibility and clarity. However, if you use branch protection on `main`, you can't push changes directly—even automated ones. The solution is to automate the version bump **by opening a pull request** after your release. And to keep your repository clean, you can also **automate the deletion of the `next` branch** after merging. Here’s how to do both with just GitHub Actions, bash, and Python.

---

### **Why Do This?**

* **Ensures `pyproject.toml` version always matches the deployed release.**
* **Works with branch protection:** No direct pushes to `main`, only PRs.
* **Cleans up old branches:** The `next` branch is automatically deleted after merging.
* **No extra dependencies or bots required—just bash, Python, and GitHub Actions.**
* **Zero manual tagging or version bumps after this setup—completely automated!**

---

### **Release Flow (How To Guarantee the Bump Happens After Deployment)**

To avoid version drift and guarantee your deployed release matches `main`, **the version bump workflow should run only after a deployment tag is created and pushed.**
That means:

1. **Your CI/CD deploy job first tests, builds, and uploads your package to PyPI (or equivalent).**
2. **Only after a successful deploy, the workflow tags the commit** (e.g., `v1.2.3`) and pushes the tag—**automatically in the deploy job**.
3. **The push of this tag triggers the version bump workflow,** which creates a PR to update `pyproject.toml` on `main` (if needed).

**This guarantees that no version bump happens until you know deploy has succeeded. There’s no manual tagging anymore!**

---

#### **Checklist: What to Avoid and What to Fix**

* Don’t tag before deploying or before tests run.
* Don’t manually push tags after deploy—you want CI/CD to handle it every time.
* Add the tag and push step as the very last step of your deploy job (see below).
* Trigger the bump-version workflow only on tag pushes (`v*.*.*`), not on normal pushes.
* Ensure your workflow has permissions to push tags (see below).
* Double-check your version extraction logic.

---

#### **Sample: How to Tag Automatically After Deploy in CI/CD**

At the *end* of your deploy job, after upload, add:

```yaml
      - name: Tag release
        if: success()
        run: |
          VERSION=$(python3 -c "import toml; print(toml.load(open('pyproject.toml'))['project']['version'])")
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"
          git tag v$VERSION
          git push origin v$VERSION
```

> **Tip:**
> Make sure your workflow has the right permissions for pushing tags:
>
> ```yaml
> permissions:
>   contents: write
> ```
>
> at the top level of your workflow YAML.

---

### **Workflow Overview**

1. **Push or merge to `main` as usual**—your CI/CD pipeline runs (`test` → `build` → `deploy`).
2. **After a successful deploy and upload, the CI/CD job creates and pushes the release tag** (e.g., `v1.2.3`).
3. **The tag push triggers the version bump workflow:**

   * Checks out `main`
   * Reads the latest tag/version
   * Updates the `pyproject.toml` version field
   * Commits and pushes the change to a new branch
   * Opens a PR to `main` (which can be auto-merged or reviewed)
4. **After the version bump PR is merged,**

   * GitHub Actions automatically deletes the `next` branch from the remote.

---

### **Documentation Timing: When to Update README and Changelog**

* **Update your README *before* release:**
  Make sure your README is up-to-date in the PR or commit before triggering your CI/CD deploy and tag. This ensures the correct README is included on PyPI and visible to users immediately.

* **Update your changelog *after* release (if it’s generated from GitHub release notes):**
  If your changelog is based on auto-generated GitHub release notes, copy them into `CHANGELOG.md` after the tag/release is created. This means the in-repo changelog will always be one release behind, which is normal if you follow this workflow.

---

### **Step-by-Step Setup**

#### **1. Ensure the GitHub CLI (`gh`) is Available**

`gh` comes pre-installed on GitHub Actions runners.
(If you use another CI: install it before running the PR command.)

---

#### **2. Add the GitHub Actions Workflow for Version Bumping**

**File:** `.github/workflows/bump-version.yml`

```yaml
name: Post-release: Bump pyproject.toml Version

permissions:
  contents: write

on:
  push:
    tags:
      - 'v*.*.*'         # Triggers on new version tags like v1.2.3

jobs:
  bump-version:
    runs-on: self-hosted

    steps:
      - name: Checkout main
        uses: actions/checkout@v4
        with:
          ref: main

      - name: Ensure gh CLI is installed
        run: |
          if ! command -v gh &> /dev/null; then
            echo "gh not found, installing..."
            # Install GitHub CLI
            if [[ "$RUNNER_OS" == "Linux" ]]; then
              type -p curl >/dev/null || sudo apt-get install curl -y
              curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg
              sudo chmod go+r /usr/share/keyrings/githubcli-archive-keyring.gpg
              echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null
              sudo apt-get update
              sudo apt-get install gh -y
            elif [[ "$RUNNER_OS" == "macOS" ]]; then
              brew install gh
            else
              echo "Unsupported OS for automatic gh install" && exit 1
            fi
          else
            echo "gh is already installed"
          fi

      - name: Get version from tag
        id: get_tag
        run: |
          TAG=${GITHUB_REF##*/}
          VERSION=${TAG#v}
          echo "version=$VERSION" >> $GITHUB_OUTPUT

      - name: Update pyproject.toml version
        run: |
          VERSION="${{ steps.get_tag.outputs.version }}"
          python3 -c "
import toml
py = 'pyproject.toml'
d = toml.load(py)
d['project']['version'] = '${VERSION}'
toml.dump(d, open(py, 'w'))
"

      - name: Create version bump branch
        run: |
          git checkout -b bump-version/v${{ steps.get_tag.outputs.version }}
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"
          git add pyproject.toml
          git commit -m "chore: bump version to v${{ steps.get_tag.outputs.version }}"
          git push origin bump-version/v${{ steps.get_tag.outputs.version }}

      - name: Create Pull Request
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          gh pr create --title "chore: bump version to v${{ steps.get_tag.outputs.version }}" \
            --body "Automated version bump after release." \
            --head bump-version/v${{ steps.get_tag.outputs.version }} \
            --base main

```

---

## **Step 3: Automate Tag Creation in Your Deploy Job**

### **Action:**

Add the following to the **end of your deploy job** in `.github/workflows/ci-cd.yml` (or whatever your CI workflow file is called):

```yaml
      - name: Tag release
        if: success()
        run: |
          VERSION=$(python3 -c "import toml; print(toml.load(open('pyproject.toml'))['project']['version'])")
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"
          git tag v$VERSION
          git push origin v$VERSION
```

**You should also ensure this is present near the top of your workflow file:**

```yaml
permissions:
  contents: write
```

This gives the workflow permission to push tags.

* * *

### **Where to add:**

* Place this step **after your deploy/upload to PyPI** in the `deploy` job, as the very last step.
    

* * *

### **What happens now:**

* After a successful deploy, your workflow will:
    
    1. Extract the version from `pyproject.toml`.
        
    2. Tag the commit as `v<version>`.
        
    3. Push the tag to GitHub.
        
* **That tag will then trigger the `bump-version.yml` workflow** you added in Step 2.
    

* * *

## **Step 4: Add “Delete `next` Branch After Merge” Workflow**

This workflow keeps your repo tidy by **automatically deleting the `next` branch** after it’s merged into `main`.

* * *

### **Action: Add the following workflow file to your repo:**

**File:** `.github/workflows/delete-next.yml`

```yaml
name: Delete next branch after merge

permissions:
  contents: write

on:
  pull_request:
    types: [closed]
    branches:
      - main

jobs:
  delete-next-branch:
    if: github.event.pull_request.merged == true && github.event.pull_request.head.ref == 'next'
    runs-on: self-hosted
    steps:
      - name: Ensure gh CLI is installed
        run: |
          if ! command -v gh &> /dev/null; then
            echo "gh not found, installing..."
            if [[ "$RUNNER_OS" == "Linux" ]]; then
              type -p curl >/dev/null || sudo apt-get install curl -y
              curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg
              sudo chmod go+r /usr/share/keyrings/githubcli-archive-keyring.gpg
              echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null
              sudo apt-get update
              sudo apt-get install gh -y
            elif [[ "$RUNNER_OS" == "macOS" ]]; then
              brew install gh
            else
              echo "Unsupported OS for automatic gh install" && exit 1
            fi
          else
            echo "gh is already installed"
          fi

      - name: Delete next branch
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          gh api -X DELETE \
            "repos/${{ github.repository }}/git/refs/heads/next"

```

* * *

### **How it works:**

* Runs every time a PR is closed on `main`.
    
* If the PR was **merged** and **the source branch was `next`**,  
    it deletes the `next` branch from your GitHub repo.
    

* * *

### **What to do:**

* Copy the above YAML into `.github/workflows/delete-next.yml` in your repo.
    

---

### **Optional: Handle Multiple Files**

If you need to bump versions in **other files** (like `setup.cfg`, or docs), just add more `python` or `sed` steps before the commit.

---

### **Dependencies**

* Uses only `python3`, the [`toml`](https://pypi.org/project/toml/) library (included on GitHub runners), and `gh` CLI.
* Works with any standard `pyproject.toml` layout.

---

## **FAQ**

**Q: Can the `next` branch deletion be restricted to only specific PRs?**
A: Yes. The example workflow only deletes `next` if the merged PR’s source branch was named `next`.

**Q: Can the version bump PR auto-merge?**
A: Yes! You can set up GitHub branch protection or bot rules to auto-merge trusted PRs from your workflow/bot user.

**Q: Does this replace manual version bumping?**
A: Yes, for releases. For pre-releases or feature development, you may still bump manually as needed.

**Q: Can I trigger this only for certain tags?**
A: Adjust the `tags:` pattern in the workflow trigger as needed.

---

## **Summary Table**

| Step                           | What Happens                              |
| ------------------------------ | ----------------------------------------- |
| CI/CD deploys and uploads      | Package is live and release tag is pushed |
| Tag pushed                     | Triggers version bump workflow on main    |
| Bump version in pyproject.toml | Branch, commit, and PR is created         |
| Merge PR to main               | Main is now fully up-to-date              |
| Merge PR from `next`           | `next` branch is deleted automatically    |

---

## **References**

* GitHub Actions: Using the GitHub CLI (`gh`)
* Keep a Changelog
* Semantic Versioning

---

**Now your `pyproject.toml` will always match your latest release, your branch protection rules are respected, your workflow stays fully automated and auditable—and your `next` branch is cleaned up after every release! No manual tags, no manual version bumps, no extra tools needed.**

---


