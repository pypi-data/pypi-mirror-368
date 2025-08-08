# Ad Hoc Tasks vs Maintenance Tasks

**How the obk CLI Organizes Real-World Software Work**

Software development is a continual balancing act between **new, urgent needs** and **the health of the codebase**. The obk CLI embraces this reality by providing distinct, structured workflows for what it calls **ad hoc tasks** and **maintenance tasks**. Here’s how they differ—and how `obk` helps keep both in check.

* * *

## What Are Ad Hoc Tasks?

**Ad hoc tasks** are one-off, situational pieces of work that arise unpredictably:

* They address **specific bugs**, implement **individual features**, or respond to **unique user requests**.
    
* They’re often high-priority and context-driven.
    
* The scope and requirements are defined in response to immediate needs, not as part of regular cadence.
    

**Examples:**

* Fixing a critical bug reported by a user
    
* Adding a feature requested in a support ticket
    
* Writing a data migration for a single release
    
* Resolving a merge conflict after an upstream change
    

* * *

## What Are Maintenance Tasks?

**Maintenance tasks** are the _routine, recurring_ activities that keep a codebase stable, clean, and efficient:

* These tasks are planned and often repeat at regular intervals (weekly, monthly, quarterly).
    
* Their scope is broader: not to change features, but to improve code health, reduce technical debt, and ensure consistency.
    

**Examples:**

* Linting and formatting codebase with tools like `ruff` and `black`
    
* Upgrading or cleaning dependencies
    
* Refactoring old patterns
    
* Removing unused code and files
    
* Updating documentation
    

* * *

## How obk CLI Distinguishes and Organizes Tasks

The **obk CLI** is built around the principle of _single-entry, prompt-driven, tracked development_. It leverages an **agents.md** configuration to separate responsibilities and workflows for different task types.

### 1. **Agents.md as a Source of Truth**

In `agents.md`, each kind of agent (script, check, or command) is listed with a purpose—this forms the automation backbone for both ad hoc and maintenance tasks. Example agents:

```markdown
# AGENTS.md

test-runner         Run all tests                 scripts/run_tests.py
formatter           Format code                   scripts/format_code.py
linter              Lint code                    scripts/lint_code.py
dependency-checker  Check dependencies            scripts/check_dependencies.py
release-manager     Manage releases/changelog     scripts/release.py
```

* **Maintenance agents**: `formatter`, `linter`, `dependency-checker`
    
* **Ad hoc/feature agents**: `test-runner`, `release-manager`, custom scripts
    

### 2. **Prompt-Driven Workflows**

* **Maintenance tasks** are run via structured prompts, referencing specific agents for repetitive, codebase-wide operations.  
    Example: `obk agent formatter` to format the codebase before every release.
    
* **Ad hoc tasks** are created as prompt documents or issue-tracked tasks, typically one-off branches that go through the `obk` stack. The prompt specifies the entry point and any agent the workflow depends on (e.g., `test-runner`).
    

### 3. **Allowed File Changes and Explicit Boundaries**

* **Maintenance task prompts** strictly list which files can be changed (e.g., `.py`, `pyproject.toml`, `.ruff.toml`, etc.).
    
* **Ad hoc task prompts** are more flexible, scoped to the specific feature or fix.
    

### 4. **Tracking and History**

* All tasks (ad hoc or maintenance) are tracked and versioned through prompts, branches, and conventional commits—ensuring transparent, reviewable history.
    

* * *

## Why Does This Matter?

Distinguishing between **ad hoc** and **maintenance** tasks:

* **Reduces chaos**—urgent fixes don’t crowd out code health.
    
* **Prevents technical debt**—maintenance tasks don’t get perpetually delayed.
    
* **Enables automation**—by formalizing common maintenance as agents, anyone (or any agent) can keep the project tidy.
    
* **Improves onboarding**—clear task categories make it easier for contributors to pick up the right work.
    

* * *

## Conclusion

The **obk CLI** doesn’t just help you get things done; it helps you get the _right_ things done, in the right way. By organizing your work into **ad hoc** and **maintenance** tasks—with a single entry point and a shared, agent-driven workflow—it lets your project stay responsive _and_ robust.

* * *