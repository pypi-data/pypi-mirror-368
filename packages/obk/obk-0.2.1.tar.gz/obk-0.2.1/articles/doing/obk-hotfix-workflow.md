# OBK Hotfix Workflow

## Overview

The OBK Hotfix Workflow is a standardized process for introducing urgent or patch-level fixes directly to the stable codebase (`main`).
This workflow ensures that emergency changes are delivered to users as quickly and safely as possible, while keeping development history clean and ensuring all improvements are reflected in ongoing feature work on `next`.

---

## Step-by-Step Workflow

1. **Start a Hotfix Branch from `main`**

   * Name: `hotfix/x.y.z-short-description` (where `x.y.z` matches the intended fix release version).
   * Pull the latest `main` to ensure your base is up to date:

     ```bash
     git checkout main
     git pull origin main
     git checkout -b hotfix/x.y.z-short-description
     ```

2. **Implement and Test the Hotfix**

   * Make and commit only the minimal necessary changes to resolve the urgent issue.
   * Add or update tests to confirm the fix.
   * If possible, keep the branch focused—avoid unrelated refactors or improvements.
   * Run all tests (automated and acceptance, as applicable) to confirm stability.

3. **Review Commit Message (with Agent Assistance)**

   * Send task `task-commit-message-conventions.md` to agent to maintain conventions.
   * Use a chat agent (such as ChatGPT) to review or help draft a clear, conventional commit subject and body.
   * Ensure the message accurately summarizes the hotfix and is ready for changelog/release tooling.

4. **Open a PR from `hotfix/x.y.z-short-description` to `main`**

   * Use conventional commit prefixes (`fix:`, `chore:`, etc.) as appropriate.
   * PR title should clearly indicate this is a hotfix release.
   * Make sure all CI checks pass.

5. **Merge the Hotfix to `main` and Tag the Release**

   * Use a squash merge to maintain clean history.
   * Use a `[patch]` tag in the squash-merge commit message to trigger deployment automation and release tagging (per project conventions).
   * Confirm the hotfix is deployed and users are notified, if relevant.

6. **Update `pyproject.toml` Version via Automation**

   * After the release, automation should open a PR against `main` to bump the version in `pyproject.toml` (if not already handled).
   * Merge this PR to ensure `main` reflects the correct released version.

7. **Propagate the Hotfix to `next`**

   * Once the hotfix is merged to `main` and the version is updated, update `next` to ensure all ongoing feature development includes the hotfix:

     ```bash
     git checkout next
     git pull origin next
     git rebase main
     git push origin next
     ```
   * Resolve any conflicts and confirm all tests pass.
   * Feature branches based on `next` should rebase as needed.

---

## Best Practices

* **Hotfixes must be focused and minimal:** Avoid introducing new features or unrelated changes.
* **Tests are required:** Every hotfix should include tests confirming the fix and preventing regressions.
* **Keep main stable:** Only hotfixes and release automation should go directly to `main`. All other work goes through `next`.
* **Propagate hotfixes immediately:** Ensure `next` is up to date with any fixes made to `main`.
* **Use automation for version bumps and changelogs:** Keep manual steps minimal and history clear.

---

## References

* [OBK Feature Workflow Guide](obk-feature-workflow-guide.md)
* [Prompt Template for Codex Agents](prompt-template-for-codex-agents.md)
* [task-commit-message-conventions.md](task-commit-message-conventions.md)

---

Let me know if you want a "quick start" checklist or visual diagram for the hotfix process!
