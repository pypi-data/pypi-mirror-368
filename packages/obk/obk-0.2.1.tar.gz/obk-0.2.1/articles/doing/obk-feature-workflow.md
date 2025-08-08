# OBK Feature Workflow

## Overview

The OBK Feature Workflow is a standardized process for developing and integrating new features into the OBK project.
All feature development branches are based on `next`—never directly on `main`.
This workflow focuses on clarity, agent-driven automation, testability, and reproducible history.

---

## Step-by-Step Workflow

1. **Write an Article for the Feature** 
   * Describe the feature you want to integrate.    
   * Organize articles in your working branch under `todo`, `doing`, `done`, or relevant subfolders. 
2. **Start a Feature Branch from `next`**   
      * **If the `next` branch does not exist, start one and `--allow-empty` commit
        * "chore: establish empty commit to maintain branch stack"
   * Then base your feature branch from `next`.     
   * Name: `feature/short-description`  
   * Pull from `next` first to ensure you’re up to date.   
3. **Add the Article to Your Feature Branch**   
4. **Start a Codex Automation Branch from the Feature Branch**  
   * Name: `codex-automation/short-description` 
5. **Create a New Prompt File Using the Prompt Template**      
   * Duplicate [Prompt Template for Codex Agents](prompt-template-for-codex-agents.md).    
6. **Draft Acceptance Tests in the Prompt** 
   * Write CLI commands or shell one-liners that represent desired behaviors and edge cases.   
   * Add to the `<gsl-acceptance-test>` section.    
7. **Write an Ad-Hoc Task for Codex Using the Adhoc Task Template** 
   * Use [Adhoc Task Template for Codex Agents](adhoc-task-template-for-codex-agents.md).    
   * Reference your prompt’s `<gsl-acceptance-test>` section and feature article.   
    Clearly define allowed/prohibited modifications and step-by-step agent actions. 
8. **Send the Directive in Codex Chat**     
   * “Execute directives in task \[task-file-name]” via Codex.  
9. **Review Generated Code Options**    
   * Codex may generate multiple candidate implementations. 
   * Review and select the best for integration.        
10. **Create a PR with the Chosen Code**    
11. **Start a Codex Cross-Review Branch**
    * Name: `codex-cross-review/short-description`  
    * Base on `codex-automation/short-description`  
12. **Iterate on Testing**  
    * Run `pytest`. Add tests to achieve 100% coverage (or close to it).    
    * Perform manual acceptance tests as defined in `<gsl-acceptance-test>`.    
    * Convert stable manual tests to automated (pytest) tests.      
13. **Final Review of Prompt and Work** 
    * Ensure the `<gsl-acceptance-test>` section contains all relevant tests.   
    * Check for unique test IDs, clear agent/human boundaries, and all required prompt sections are present and clear.  
14. **Merge Back to codex-automation/short-description**    
15. **Merge codex-automation/short-description to feature/short-description & Push**    
16. **Squash Commits and Review Commit Message (with Agent Assistance)**    
17. **Open a PR from `feature/short-description` to `next`**     
> **This completes the feature workflow. The release and integration of `next` to `main` are handled in a separate process.**

---

## Best Practices

* **Manual, one-line tests come first:** Prove value manually, then automate.
* **Always use the Prompt and Ad-Hoc Task Templates:** Maintain clarity and discipline.
* **Branch naming consistency:** For feature, automation, and cross-review branches.
* **Merge feature branches only into `next`, never directly to `main`.**
* **Regularly merge/rebase from `next` to keep feature branches current.**

---

## References

* [Prompt Template for Codex Agents](prompt-template-for-codex-agents.md)
* [Why One-Line Manual Tests Should Precede Automation](one-line-manual-tests.md)
* [Adhoc Task Template for Codex Agents](adhoc-task-template-for-codex-agents.md)

---


## Addendum: Adapting the Feature Workflow for Teams

**The OBK Feature Workflow is designed to scale seamlessly to team collaboration. To ensure smooth operation in a multi-contributor environment, observe the following additional practices:**

* **Each team member creates their own feature branch from `next`:**  
    All new features, improvements, or fixes should be developed in a dedicated branch (e.g., `feature/short-description`) based on the current `next` branch, never directly on `main`.
    
* **Responsibility for rebasing/merging from `next`:**  
    Each contributor is responsible for regularly rebasing or merging from `next` into their feature branch, especially before opening a PR. This keeps their work current with all other ongoing changes and reduces the risk of integration conflicts.
    
* **Frequent communication:**  
    Team members should communicate planned merges, rebases, or significant changes in a shared channel (e.g., Slack, Teams, or project board) to coordinate work and avoid overlap.
    
* **Branch protection and PR review:**  
    Protected branch settings should require at least one reviewer for all PRs to `next`. Automated checks (CI, lint, tests) must pass before merging.
    
* **PR ownership and cleanup:**  
    The team member who opens a PR is responsible for responding to feedback, rebasing if conflicts arise, and ensuring the branch history is clean before merge.
    
* **No direct pushes to `next` or `main`:**  
    All changes must go through the PR process. Direct pushes are strongly discouraged or disabled by branch protection.
    

**Summary:**

> In a team context, all contributors independently manage their feature branches off `next`, regularly rebase or merge from `next` to stay up to date, and integrate via PRs—ensuring quality, clarity, and minimal conflict.
