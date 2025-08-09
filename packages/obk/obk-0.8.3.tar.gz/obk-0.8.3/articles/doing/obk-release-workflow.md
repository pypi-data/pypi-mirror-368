# OBK Release Workflow

## Overview

The OBK Release Workflow governs all official deployments to PyPI from the `main` branch.
It ensures every release is deliberate, tested, and documented, with full control using protected PRs, explicit commit-message triggers, and automated post-release maintenance for accuracy.

---

## Step-by-Step Release Workflow

1. **Prepare and Merge Features to `next`**

   * Complete feature development and merge PRs to `next` as described in the OBK Feature Workflow.
   * Confirm all tests and status checks pass before proceeding.

2. **Review, Edit, and Squash Commits in `next`**

   * Review the commit history on `next` and squash or edit commits as necessary for clarity.
   * Combine chore/doc/cleanup commits into logical changesets for a clean history.
   * Ensure each commit is well-labeled and ready for release.

3. **Generate Release Notes**

   * Use the GitHub Release **Generate release notes** button to create a draft of the release notes.
   * Review and edit the release notes for clarity and accuracy.

4. **Update Changelog and Documentation in `next`**

   * Update `CHANGELOG.md`, `README.md`, and any relevant documentation to match the finalized release notes.
   * Summarize user-facing changes, bugfixes, and enhancements.
   * These doc and changelog updates can be squashed into the last commit for release.

5. **Open a Release PR from `next` to `main`**

   * Create a pull request from the `next` branch to the `main` branch.
   * Use the PR checklist to confirm everything is release-ready.
   * Instruct reviewers to look for `[patch]` or `[minor]` in the relevant commit messages.

6. **Final Review and Approval**

   * Reviewers confirm:

     * Tests pass
     * Documentation and changelog are up to date
     * All changes are release-ready and well-documented

7. **Rebase-and-Merge to `main` (with `[patch]` or `[minor]`)**

   * **Use “Rebase and Merge” in the GitHub PR UI** for the release PR from `next` to `main`.
   * This preserves all commits from `next` and adds them individually to `main`, keeping your organized history.
   * Ensure the final commit(s) include `[patch]` or `[minor]` in their messages (e.g., `feat: add feature x [patch]`).
   * Omit `[patch]`/`[minor]` for non-release PRs (CI will test/build but skip deploy).

8. **CI/CD Pipeline Executes**

   * **Test:** Run all tests (`pytest`, lint, etc.).
   * **Build:** Build the distribution package.
   * **Deploy:**

     * **Only runs if `[patch]` or `[minor]` is in the commit message**
     * Bumps the version in `pyproject.toml` (local to runner)
     * Uploads to PyPI via Twine using repository secrets.
   * Any test or build failure halts deploy.

9. **Verify PyPI Publication**

   * Confirm the new version is available on [PyPI](https://pypi.org/).
   * Optionally, install and test from PyPI to verify.

---

## Key Policies and Notes

* **Deploys Only from `main`:**
  The `main` branch is the only deploy branch—no other branch may publish to PyPI.

* **Commit-Message-Driven Deploy:**
  The `[patch]` or `[minor]` tag in a commit message is **required** for PyPI publish; all other merges are non-deployment.

* **Branch Protection Enforced:**
  All merges to `main` must be via PR, with required status checks and reviews.

* **Release PR merge method:**
  The repository only allows “Rebase and Merge” for PRs (especially from `next` to `main`). “Squash and Merge” is disabled to preserve organized commit history for each release cycle.

* **Automated Version Bump:**
  Each deploy triggers an automated PR to update the version in `pyproject.toml` post-release.

* **Post-Release Maintenance:**
  After every release, confirm the version update PR is merged and release notes are accurate.

* **Changelog and Release Notes:**
  Use GitHub’s **Generate release notes** button, and update `CHANGELOG.md` as needed.

---

## References

* [main-branch-pypi-cd-scaffold.md](main-branch-pypi-cd-scaffold.md)
* OBK Feature Workflow
* [PR Template](.github/pull_request_template.md)
* [CI/CD Pipeline](.github/workflows/ci-cd.yml)
* [PyPI Token Setup](https://pypi.org/help/#apitoken)

---

## Summary

**Every OBK release is:**

* Fully reviewed and tested before merging to `main`
* Explicitly triggered via `[patch]` or `[minor]` in the commit message
* Version-bumped and published only if tests/build pass
* Synchronized post-release with accurate versioning and documentation

*This process is frozen until future team consensus and documentation update.*
