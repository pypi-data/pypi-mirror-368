## \[Commit Task] Generate a Conventional Commit Message from Code Diffs

**Objective:**
Write a single, high-quality commit message (subject and body) describing the current code diffs. The commit message must strictly adhere to the following conventions:

---

### **Commit Message Conventions**

1. **Subject line** must use the [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) format (e.g., `feat: add robust and scalable unit test framework`).
2. **Subject line must not exceed 100 characters.** (Enforced by `commitlint`.)
3. **Do not use backticks in the subject line.** Backticks are reserved for the body bullets only.
4. **Subject** must be driven entirely by code, configuration, test, and CI changes—**not** by documentation or article content.
5. **Body** must be written in plain English, lowercase, with no sentence-ending periods (except when required for clarity, e.g., file names).
6. **No conventional commit prefixes** (e.g., `feat:`, `ci:`) are allowed in the body; use only in the subject.
7. **Use backticks** for all commands, file paths, and configuration keys (e.g., `pytest`, `.gitignore`, `pyproject.toml`).
8. **One change per bullet point**—each code/config change gets its own bullet for clarity.
9. **No references** to issue or pull request numbers in either the subject or body.
10. **Do not describe documentation or article contents** in the subject or body.
11. **Each bullet must start with a lowercase action verb** for parallel, concise structure (e.g., `add`, `implement`, `consolidate`, `update`).
12. **No sentence capitalization in bullets**—start each with a lowercase letter.
13. **If articles or markdown files are added, moved, or changed,** include this exact bullet at the end of the body, regardless of content:
    `- maintain planning, usage, and project guidance articles`
14. **Do not nest or embed previous commit messages** in the body, even when squashing multiple commits. Instead, write a single, flat summary that represents the changes as a cohesive whole.

---

**Instructions:**
Analyze the code diffs. Write the commit message (subject and body) strictly following the conventions above.
Only use code, configuration, and test changes to drive the subject and body content.
If articles or markdown files are present in the diff, include the fixed bullet at the end of the body—do **not** describe their content.

---
