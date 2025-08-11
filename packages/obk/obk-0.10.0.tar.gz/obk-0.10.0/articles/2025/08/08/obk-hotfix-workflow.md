# OBK Hotfix Workflow

---

## Overview

This document explains how to prepare, review, and release a hotfix for OBK using the tag-triggered, main-only deploy model.
A hotfix is an urgent patch to fix critical bugs or security issues that must be released outside the normal feature cycle.

---

## Hotfix Workflow

### 1. Branch from `main`

* Start a new branch from the latest `main`:

  ```bash
  git checkout main
  git pull
  git checkout -b hotfix/your-brief-description
  ```
* You do **not** need to bump the version at this point.

---

### 2. Make Your Hotfix Changes

* Apply the minimal patch necessary to fix the issue.
* Add or update tests to confirm the fix.

---

### 3. Open a Pull Request to `main`

* When the fix is ready, open a PR from your hotfix branch to `main`.
* Make sure all tests pass and reviewers approve.
* **Squash and merge** when ready (produces one clear commit).

---

### 4. Bump the Patch Version in `pyproject.toml`

* After the fix is merged, bump the version in `pyproject.toml` to the next patch version (e.g., from `1.2.3` to `1.2.4`).
* Commit and merge this as the **very last, squashed commit** before release.

---

### 5. Create and Push a Release Tag

* Create a Git tag matching the new patch version:

  * Format: `vX.Y.Z` (e.g., `v1.2.4`)
* Push the tag to GitHub.

  ```bash
  git tag v1.2.4
  git push origin v1.2.4
  ```
* This tag triggers the CI/CD pipeline for deployment.

---

### 6. Deployment

* The pipeline will:

  * Validate the `pyproject.toml` version matches the tag.
  * Build, test, and deploy to PyPI **only if the versions match**.
* If there’s a mismatch, deployment is blocked and you’ll see a clear error.

---

## Summary Checklist

* [ ] Branch from `main`
* [ ] Commit, test, and PR your hotfix
* [ ] Squash merge to `main`
* [ ] Bump patch version in `pyproject.toml` as the last commit
* [ ] Merge version bump to `main`
* [ ] Create and push matching tag (e.g., `v1.2.4`)
* [ ] CI/CD validates and deploys to PyPI

---

## Best Practices

* **Keep hotfixes minimal**—avoid refactoring or adding unrelated changes.
* **Only bump the version in the final commit before tagging.**
* **No `next` branch or commit-message triggers.**
* **Review and test thoroughly.** Even for urgent hotfixes, CI must pass before release.

---

## FAQ

**Q: Can I prepare more than one hotfix at a time?**
A: Yes, but bump the patch version and tag *after* merging each hotfix to `main`, and ensure each has a unique version number.

**Q: What if I forget to bump the version before tagging?**
A: The workflow will fail and warn you. Bump the version, merge, and re-tag.

**Q: Should I use a `hotfix/` prefix?**
A: Optional—no strict naming conventions. Use whatever helps you track work.

---

## References

* [OBK Feature Workflow](obk-feature-workflow.md)
* [OBK Release Workflow](obk-release-workflow.md)
* [Tag-Triggered Deploy Article](#)
