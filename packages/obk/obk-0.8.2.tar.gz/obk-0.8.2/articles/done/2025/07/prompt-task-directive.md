# 🗭 The Difference Between a Prompt, a Task, and a Directive

In intelligent agent systems like OBK, you’ll often see the words **prompt**, **task**, and **directive**. It’s easy to assume each has a clear technical meaning, but in practice, the lines blur. Sometimes a “directive” is part of a prompt; sometimes a task contains multiple directives. So, what’s the real difference—and how does OBK handle it?

Let’s break it down.

* * *

## 🔀 Same Content, Different Roles

A **prompt**, a **task**, and a **directive** might use the same language, but their roles are different.

* A **prompt** sets context, intent, and constraints for the agent.
    
* A **task** is an explicit, trackable unit of work that an agent must complete.
    
* A **directive** is an instruction or command—any of the above might contain directives.
    

It’s not about the words themselves. It’s about what _function_ those words play in the workflow.

* * *

## 🧐 Prompt vs Task: The Core Difference

|  | **Task** | **Prompt** |
| --- | --- | --- |
| **Function** | Trackable unit of work, always actionable | Sets context, constraints, or goals |
| **Form** | Explicit, stepwise instructions | Structured, often with rules/tests |
| **Tracked?** | Yes | Yes |
| **May contain a directive?** | Yes | Yes |

A **prompt** might contain tasks, background, rules, or scenarios.

A **task** is always something an agent does, often made up of one or more directives.

A **directive** is any “do this” statement, wherever it appears—but only **tasks** are now tracked as first-class OBK elements.

* * *

## 🤖 Specificity Is Relative

Specificity isn’t what divides these concepts. Both prompts and tasks can be broad or specific. The difference is in intent and traceability, not detail.

* * *

## 🗳 Prompts Contain Tasks, Tasks Contain Directives

A prompt can include one or many tasks. Each task may contain several directives (“steps”). For example:

**Prompt:**

```xml
<gsl-prompt id="20250730T062755-0400">
  <gsl-purpose>
    Implement classes in my Python project.
  </gsl-purpose>
  <gsl-tdd>
    <gsl-test id="T1">
    - T1: TBD
    </gsl-test>
  </gsl-tdd>
  <gsl-document-spec>
    Agents MUST NOT modify existing <gsl-test> entries.
    Agents MAY append new tests.
  </gsl-document-spec>
</gsl-prompt>
```

**Task (formerly “directive”):**

```
## Unified Prompt-Driven Functions to Classes Task

Objective:
Sequentially implement and test features in `obk` by reproducing behaviors from a reference article.

1. Analyze the repo.
2. Extract features from the article.
3. Write manual tests in prompt `20250730T062755-0400`.
4. Follow file modification constraints.
```

Here, the **task** is a stand-alone, tracked item that tells the agent what to do, step by step. Each step is a directive—but the task as a whole is the actionable unit.

* * *

## 📄 Specifications Can Be Directive

A specification can also include directives (rules):

```xml
<gsl-document-spec>
  Agents MUST NOT delete any <gsl-test> entries once written.
</gsl-document-spec>
```

This rule constrains agent behavior—a directive within the document, even if it’s not called out as a “directive” type.

* * *

## 🔗 How OBK Uses Prompts, Tasks, and Directives

In OBK:

* **Prompts** are the structured input/context documents.
    
* **Tasks** are the actionable, tracked units (formerly called directives in the language).
    
* **Directives** are instructions embedded inside prompts and tasks, but are no longer a tracked GSL artifact.
    

* * *

## 🔺 Final Word

The real difference is not about specificity or structure. It’s about **role and traceability**:

* **Prompt**: Sets context and rules.
    
* **Task**: Actionable, tracked unit—may contain multiple directives.
    
* **Directive**: Any instruction, wherever it appears.
    

**In OBK, tasks and prompts are tracked. Directives are instructions, not artifacts.**

Traceability and intent matter more than rigid categories.

* * *