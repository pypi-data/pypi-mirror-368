# Keep the PR Open: Iterate on the Branch Until It’s Green

The core idea: **don’t close a pull request when tests fail.** Keep the PR open, keep pushing fixes to the same feature branch, and iterate until checks are green—then merge. Close only if you’re abandoning or pivoting.

* * *

## Why this workflow?

* **Fast feedback.** Draft PRs trigger CI early.
    
* **Single source of truth.** One thread holds code, review, and CI history.
    
* **Stable main.** Branch protection blocks merges until checks pass.
    
* **Less thrash.** No close/reopen churn, fewer re-orientations for reviewers.
    

* * *

## Prerequisites

* **CI on PRs** (tests + lint run automatically).
    
* **Branch protection** (require checks before merge).
    
* **PR template** in the repo (see below).
    
* Optional but nice:
    
    * **Local parity scripts** (e.g., `make test`, `scripts/test.sh`, or `./gradlew test`) so devs can reproduce CI locally.
        
    * **Pinned dependencies** or an offline/install script for reproducible runs.
        

* * *

## Recommended PR Template

Put this at `.github/PULL_REQUEST_TEMPLATE.md` so every PR starts with the right info:

```markdown
# What
- Brief, imperative summary (“Add X”, “Fix Y”)

# Why
- User value or problem statement

# How
- Key technical changes (schemas, public APIs, migrations)
- Any risk/compatibility notes

# Test Plan
- [ ] Unit tests updated/added
- [ ] Integration/e2e where applicable
- [ ] Repro steps for bug fixes
- Include commands to run locally (e.g., `make test`)

# Checklists
- [ ] CI green (tests + lint)
- [ ] Docs/help text updated (if user-facing)
- [ ] Rollback plan noted (how to revert safely)

# Screenshots / Logs (optional)
- Paste relevant output or UI changes
```

> Tip: If you have multiple PR types, use **PR template chooser** (`.github/PULL_REQUEST_TEMPLATE/feature.md`, `bugfix.md`, etc.).

* * *

## The Workflow (Step-by-Step)

### 1) Create a feature branch

```bash
git checkout -b feat/short-slug
```

### 2) Open a **Draft PR** early

* Title: `feat: <concise summary>`
    
* Fill the PR template (What/Why/How/Test Plan).
    
* Mark as **Draft** so reviewers know it’s WIP.
    

### 3) Push, let CI run

```bash
git add -A
git commit -m "feat: initial scaffold"
git push -u origin feat/short-slug
```

Expect red at first—totally fine.

### 4) If CI is red, **iterate on the same PR**

* **Reproduce locally** with the same commands CI uses (e.g., `make test`, `npm test`, `./gradlew test`).
    
* **Fix code or tests**; keep commits small.
    
* Push again:
    
    ```bash
    git commit -m "fix: align output with spec"
    git push
    ```
    
* CI re-runs. Repeat until green.
    

### 5) Convert to “Ready for review”

* When checks pass and scope matches the goal, flip from Draft to Ready.
    
* Address review comments with additional commits (squash at the end if you want a tidy history).
    

### 6) Merge

* Prefer **Squash & merge** to keep history clean (or autosquash `--fixup` commits).
    
* Delete the branch if your team prefers.
    

### 7) Only close if you pivot

* Close with a short note and link to the successor issue/PR if you’re changing approach or dropping the work.
    

* * *

## What “Iterate” Looks Like

**Typical loop when tests fail**

1. Read the failing job: test name, error, stack trace, logs.
    
2. Reproduce locally with the same command CI uses.
    
3. Decide whether the **code** or the **test** is wrong.
    
4. Push a focused fix; watch CI.
    

**CI-only failures**

* Check environment mismatches (OS, Python/Node/JDK version, env vars).
    
* Ensure dependencies and tools are pinned.
    
* Rebuild fresh (no cache) to catch missing steps.
    

**Flaky tests**

* Deflake by fixing shared state, timeouts, order-dependence.
    
* If unavoidable short-term, mark flaky with a link to an issue and unflake later.
    

* * *

## Checklists

### Before opening a PR

*  Small, focused branch
    
*  PR template filled (What/Why/How/Test Plan)
    
*  Tests run locally
    

### When CI fails

*  Reproduce locally with the same command
    
*  Root cause identified
    
*  Fix committed; CI re-run
    
*  PR description updated if behavior intentionally changed
    

### Before merging

*  All checks green
    
*  Review comments addressed
    
*  Docs/help updated if user-facing
    
*  Rollback plan understood (how to revert safely)
    

* * *

## Do’s and Don’ts

**Do**

* Use **Draft PRs** early.
    
* Keep changes scoped and commits small.
    
* Make error messages stable (easy to assert in tests).
    
* Pin toolchain/dependencies for reproducible CI.
    

**Don’t**

* Close/reopen PRs just because of failures.
    
* Mix unrelated changes in one PR.
    
* Rely on local timezone or machine-specific paths in tests.
    
* Leave flaky tests unaddressed.
    

* * *

## FAQ

**Q: Tests keep failing. Close and start over?**  
A: No. Keep the PR open and push fixes to the same branch—PRs are collaboration threads.

**Q: CI is red but local is green.**  
A: Align environments (versions, env vars). Re-run locally with CI’s exact command; ensure dependency pinning.

**Q: How do PR templates fit here?**  
A: They standardize context (What/Why/How/Test Plan) so reviewers can help faster. Keep them short but structured.

**Q: When is it okay to close a PR?**  
A: When you abandon or replace the approach. Link to the new work so history stays traceable.

* * *

## TL;DR

* Open a **Draft PR** early.
    
* **Iterate on the same branch** until CI is green.
    
* Use a **PR template** to keep context crisp.
    
* **Merge when ready**; close only if you pivot.