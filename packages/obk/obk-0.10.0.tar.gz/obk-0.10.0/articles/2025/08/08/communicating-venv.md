# Best Practices for Communicating Virtual Environment (`venv`) Usage to Python Users

Virtual environments (`venv`) are a cornerstone of modern Python development. They let users isolate project dependencies and avoid version conflicts. But while most experienced developers are familiar with `venv`, not every user is — and even seasoned engineers appreciate clear, concise instructions. As a project maintainer, how you communicate `venv` usage can dramatically improve the onboarding experience for your users.

## Why Communicate About `venv`?

* **Avoid dependency conflicts:** Projects may require different versions of libraries. Virtual environments keep these isolated.
    
* **Promote reproducibility:** Clean environments help ensure “it works on my machine” also means “it works on yours.”
    
* **Prevent pollution:** Without a `venv`, global Python installs can become cluttered and error-prone.
    

## Best Practices

### 1. **Explicitly Recommend Using `venv`**

Don’t assume your users know to do this. State it clearly at the start of your install or quickstart section.

**Example:**

> “We recommend installing `obk` in a virtual environment to avoid dependency conflicts.”

### 2. **Show the Setup Steps for Different Platforms**

Not everyone uses the same shell or OS. Give instructions for Unix/macOS **and** Windows.

**Example:**

```sh
# Create a virtual environment in the project folder
python -m venv .venv

# Activate it (Unix/macOS)
source .venv/bin/activate

# ...or on Windows
.venv\Scripts\activate
```

### 3. **Keep the Instructions Simple**

Don’t over-explain. Just enough to get people started. You can always link to the official docs for more.

**Example:**

> “If you’re new to Python virtual environments, see the official venv guide.”

### 4. **Explain How to Install Your Package Once Activated**

Be explicit that `pip install ...` should be run **after** the environment is activated.

**Example:**

```sh
pip install obk
```

### 5. **Clarify Deactivation**

Optionally, mention that the environment can be deactivated with `deactivate`.

**Example:**

> “To exit the virtual environment, type `deactivate`.”

### 6. **Don’t Ship a Script (Usually)**

It’s rare to provide a script to set up `venv` unless your tool targets absolute beginners. Most users expect to do this themselves.

### 7. **Be Consistent**

Use the same variable names (`.venv` or `env`), and place your instructions near the top of your README, in a “Quickstart” or “Installation” section.

## Sample README Snippet

```markdown
## Quickstart (Recommended: Virtual Environment)

```sh
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install obk
```

If you’re new to virtual environments, see Python’s official venv documentation.

```

## Summary Table

| Step                    | Unix/macOS                      | Windows                          |
|-------------------------|---------------------------------|-----------------------------------|
| Create venv             | `python -m venv .venv`          | `python -m venv .venv`            |
| Activate                | `source .venv/bin/activate`     | `.venv\Scripts\activate`          |
| Install your package    | `pip install obk`               | `pip install obk`                 |
| Deactivate              | `deactivate`                    | `deactivate`                      |

## Final Tips

- Keep instructions minimal and near the top.
- Link to official documentation for new users.
- Be platform-aware.
- Avoid custom scripts unless absolutely necessary.

---
