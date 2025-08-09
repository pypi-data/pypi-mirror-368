# How to Setup Branch Protection In GitHub

This guide outlines how to configure branch protection in GitHub using **rulesets**. Below are the exact names and settings used in our configuration.

* * *

## Ruleset 1: `all-branches-pr-required`

**Name:** `all-branches-pr-required`  
**Target:** All branches (`*`)  
**Key Settings:**

* **Require pull request before merging:** Enabled

* **Dismiss stale pull request approvals when new commits are pushed** Enabled (New, reviewable commits pushed will dismiss previous pull request review approvals.)
    
* **Require approvals:** Enabled (number of required approvals can be customized)
    
* **Require status checks to pass before merging:** Enabled (specify status checks as needed)
    
* **Restrict who can push to matching branches:** Optional (customize as needed)
    
* **Require linear history:** Optional (enable to enforce no merge commits)
    
* **Do not allow bypassing the above settings:** Optional (tighten as needed)
    

**How to configure:**

1. Go to your repository on GitHub.
    
2. Click **Settings** > **Branches** > **Branch protection rules**.
    
3. Click **Add rule**.
    
4. For **Branch name pattern**, enter `*`.
    
5. Enable:
    
    * “Require a pull request before merging”
        
    * “Require approvals” (set number)
        
    * “Require status checks to pass before merging” (select checks)
        
6. Save the rule as `all-branches-pr-required`.
    

* * *

## Ruleset 2: `main-protection-v1`

**Name:** `main-protection-v1`  
**Target:** The `main` branch  
**Key Settings:**

* **Require pull request before merging:** Enabled

* **Dismiss stale pull request approvals when new commits are pushed** Enabled (New, reviewable commits pushed will dismiss previous pull request review approvals.)
    
* **Require status checks to pass before merging:** Enabled (specify exact required checks, e.g., `CI`, `lint`)
    
* **Require linear history:** Enabled
    
* **Require signed commits:** Optional (enable for added security)
    
* **Restrict who can push:** Enabled (define specific teams or users)
    
* **Do not allow force pushes:** Enabled
    
* **Do not allow deletions:** Enabled
    

**How to configure:**

1. Go to your repository on GitHub.
    
2. Click **Settings** > **Branches** > **Branch protection rules**.
    
3. Click **Add rule**.
    
4. For **Branch name pattern**, enter `main`.
    
5. Enable the following:
    
    * “Require a pull request before merging”
        
    * “Require status checks to pass before merging” (select required checks)
        
    * “Require linear history”
        
    * “Restrict who can push to matching branches” (add allowed users/teams)
        
    * “Do not allow force pushes”
        
    * “Do not allow deletions”
        
6. Save the rule as `main-protection-v1`.
    

* * *

## Example YAML Configuration

If using **GitHub’s branch protection API** or a configuration-as-code tool, the settings might look like this (pseudo-YAML for reference):

```yaml
branch_protection_rules:
  - name: all-branches-pr-required
    pattern: '*'
    require_pull_request: true
    required_approving_review_count: 1
    required_status_checks:
      - ci
      - lint
    restrict_pushes: false

  - name: main-protection-v1
    pattern: 'main'
    require_pull_request: true
    required_status_checks:
      - ci
      - lint
    require_linear_history: true
    require_signed_commits: true
    restrict_pushes: true
    allowed_push_users:
      - octo-admins
      - octo-bots
    allow_force_pushes: false
    allow_deletions: false
```

> **Tip:** Adjust the required status checks, allowed pushers, and approval counts to match your team’s workflow and security posture.

* * *

**Summary Table**

| Rule Name | Pattern | Require PR | Status Checks | Linear History | Restrict Pushes | Allow Force Push | Allow Deletion |
| --- | --- | --- | --- | --- | --- | --- | --- |
| all-branches-pr-required | `*` | Yes | Yes (as needed) | Optional | Optional | No | No |
| main-protection-v1 | `main` | Yes | Yes (specific) | Yes | Yes | No | No |

* * *

**References:**

* GitHub Docs: Managing a branch protection rule
    
