# **Stacked Branching in Git: How to Preserve Your Intent**

---

## **Introduction**

When working on complex features or debugging sessions, it’s common to open “stacked” branches—each branch is created off the last as new dependencies or blockers arise. However, **how and when you make commits on these branches determines whether git actually records your intended stack**, or just treats them all as floating branch names. This guide explains how to ensure your stacked branches truly reflect your workflow and the *dependency order you intended*, not just what git infers from your commit order.

---

## **1\. What Are Stacked Branches?**

-   **Definition:** A workflow where you open new branches as dependencies or blockers arise, e.g., `feature-A` → `feature-B` → `feature-C`.
    
-   **Goal:** Each branch logically depends on the last; your history should show this sequence both for yourself and future reviewers.
    

---

## **2\. What Happens If You Only Create Branches (But Don’t Commit)?**

-   All branch pointers will **point to the same commit** (usually your base, like `main` or `work`).
    
-   In GUIs (Tower, GitKraken, Sourcetree), all branch names will show up on the same commit dot.
    
-   Git **cannot know** your intended stack, since there’s no commit to mark the dependency.
    

---

## **3\. Why Does This Matter?**

-   If you start working several branches deep and only make your first commit on the third-level branch, that commit will be based off the original parent (e.g., `work`), *not* on your intermediate branches.
    
-   You lose the record of “this branch was intended to be built on top of the previous one.”
    
-   Automated tools, visualizations, and reviewers won’t see your true dependency stack.
    

---

## **4\. How to Make Your Stack Explicit**

**The solution:**  
Whenever you create a new stacked branch, **make at least one commit** (even empty) before creating the next branch.

### **Step-by-step Example**

```bash
# 1. Start from 'work'
git checkout work

# 2. Create branch-A, commit something
git checkout -b branch-A
git commit --allow-empty -m "WIP: Set up branch-A"

# 3. Create branch-B off branch-A, commit something
git checkout -b branch-B
git commit --allow-empty -m "WIP: Set up branch-B"

# 4. Create branch-C off branch-B, commit something
git checkout -b branch-C
git commit --allow-empty -m "WIP: Set up branch-C"
```

-   Now your branch pointers form a real stack:
    
    ```css
    work → branch-A → branch-B → branch-C
    ```
    
-   In Tower (or any graph viewer), you’ll see each branch pointer on a *unique* commit in sequence.
    

---

## **5\. What if I Wait to Commit?**

-   If you make several branches but only commit once you’re deep in the stack, your new commit will be a direct child of the base (e.g., `work`), and git’s history will **not reflect your logical stack**.
    
-   You can’t “fix” this after the fact (without rewriting history).
    

---

## **6\. “First Come, First Serve” Reflects Reality**

-   The order you encounter problems or needs is preserved if you make a commit at each stacking decision point.
    
-   Your intent—“I didn’t know I needed to do C until I started B”—is now visible in history.
    

---

## **7\. What Kind of Commit?**

-   It can be a real code/doc change, or just an empty placeholder:
    
    ```bash
    git commit --allow-empty -m "WIP: Stack placeholder for branch-B"
    ```
    
-   These are easily squashed or amended later, but **preserve ancestry in the meantime.**
    

---

## **8\. Visualizing Your Stack**

-   In Tower (or similar), each branch now points to a distinct commit in a clear chain.
    
-   As you add real work, you’ll see the stacked progression.
    
-   When merging, you can easily walk the dependency chain up or down.
    

---

## **9\. TL;DR / Quick Reference**

| Action | Result |
| --- | --- |
| Create branch, no commit | Branch is “floating”; stack intent is not preserved |
| Create branch, make commit | Stack is explicit; git history matches your workflow |
| Use empty commit (`--allow-empty`) | Fast, no code needed; safe to squash later |

---

## **10\. Summary**

> **If the structure of your stacked branches matters, make a commit on each branch when you create it—even if it’s just a placeholder.**  
> This makes your workflow and intent clear to yourself, collaborators, and all your git tools—now and in the future.

---

*Keep your history clean, your stacks clear, and your intent visible!*

---