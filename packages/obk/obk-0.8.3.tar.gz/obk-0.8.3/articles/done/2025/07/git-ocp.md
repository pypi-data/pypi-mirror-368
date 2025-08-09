# Git: The Only OCP You Need

* * *

## Introduction

In software engineering, the **Open/Closed Principle** (OCP) is a foundational idea:

> _"Software entities should be open for extension, but closed for modification."_

It’s one of the SOLID principles, widely promoted as a marker of good design. Yet, in most domains, OCP is more of an _aspiration_ than a guarantee. It’s something we try to practice through discipline, review, and convention—but not something the system enforces.

There’s one big exception: **Git**.

## Git: OCP by Architecture

At its core, Git is built around immutability and append-only history:

* **Commits are immutable.** Once created, a commit’s content and metadata are forever linked to its cryptographic hash. Change anything, and the hash changes.
    
* **Branches and tags extend history.** You can always add new work, create new branches, and annotate history. But the underlying data isn’t modified; it’s extended.
    
* **History can’t be quietly rewritten.** Even when you _do_ rewrite history (via rebase or filter-branch), you’re not modifying the past—you’re creating new objects with new hashes. The original chain still exists (at least until garbage collected).
    

**In other words:**  
_You literally cannot break the Open/Closed Principle in Git—at least, not without the system making it explicit and obvious._ Tampering always results in a new, distinct object.

## OCP Everywhere Else: Convention, Not Constraint

Contrast this with most other areas of software:

* In code, anyone can edit a class, function, or module.
    
* In configuration files, settings can be overwritten or deleted.
    
* In APIs, old endpoints can be refactored or removed.
    

You might _try_ to follow OCP—perhaps through code reviews, linters, or best practices—but there’s nothing fundamentally preventing you from breaking it.  
**OCP is an ideal, not an enforced rule.**

## Why This Matters

Treating a Git repository as a software component means you get OCP “for free.” You’re always building on what’s come before, never silently rewriting history.

This architectural guarantee:

* **Prevents accidental regressions**—what’s done is done.
    
* **Enables reliable auditing and traceability.**
    
* **Allows safe extension** via branching and merging.
    
* **Makes “rewriting the past” a visible, intentional act** (and never a true overwrite).
    

## The Physics of Source Control

To borrow a metaphor:

> _In code, OCP is good manners. In Git, it’s the law of physics._

You can’t modify the past—you can only create new futures. This simple, powerful constraint is a key reason Git has become the backbone of modern collaborative development.

## Conclusion

If you want to see the Open/Closed Principle enforced at a foundational level, look at Git.  
Everywhere else in software, OCP depends on your discipline, your team, and your process.  
In Git, it’s a guarantee built into the fabric of the system itself.

* * *

