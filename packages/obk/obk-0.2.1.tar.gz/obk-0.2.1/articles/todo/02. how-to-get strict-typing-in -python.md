# How to Get Strict Typing in Python

**Python** is beloved for its flexibility and expressiveness—but that flexibility comes with a cost: it’s easy for bugs to creep in due to its dynamic typing. If you want your Python codebase to have the safety and rigor of strictly-typed languages like Java or C#, this guide will show you how to get as close as possible using modern tools and best practices.

* * *

## 1. What “Strict Typing” Means in Python

Strict typing means:

* **Every variable, function, and class has an explicit type annotation.**
    
* **Code is automatically checked** for type correctness—before it runs.
    
* **Type errors are caught early,** not after bugs surface in production.
    

While Python itself is a dynamically typed language and doesn’t enforce types at runtime, the ecosystem provides powerful static analysis tools to bridge the gap.

* * *

## 2. Type Annotations: The Foundation

Python 3 supports _type hints_ via PEP 484.

**Example:**

```python
def greet(name: str) -> str:
    return f"Hello, {name}"
```

Add type annotations everywhere: function arguments, return values, class attributes, variables, etc.

* * *

## 3. Use a Static Type Checker (Mypy)

Mypy is the de facto tool for type checking in Python. It analyzes your code and reports type errors before you run your program.

**Installation:**

```bash
pip install mypy
```

**Run on your project:**

```bash
mypy .
```

* * *

## 4. Configure Mypy for “Strict” Checking

By default, Mypy is permissive. For maximum safety, enable strict mode and add checks in your `pyproject.toml` or `mypy.ini`:

```ini
[mypy]
strict = True
disallow_untyped_defs = True
disallow_incomplete_defs = True
check_untyped_defs = True
warn_unused_ignores = True
```

This configuration:

* **Requires type hints everywhere.**
    
* **Checks untyped functions and classes.**
    
* **Warns about ignored type errors.**
    

* * *

## 5. Enforce Typing with Pre-commit Hooks

You can automate type checking so no untyped or type-incorrect code is committed.

**Setup pre-commit:**

```bash
pip install pre-commit
```

**Example `.pre-commit-config.yaml`:**

```yaml
repos:
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.10.0
    hooks:
      - id: mypy
```

**Activate hooks:**

```bash
pre-commit install
```

* * *

## 6. Catch Type Issues at Runtime (Optional)

For runtime enforcement (less common), use tools like `typeguard` or [`enforce`](https://github.com/RussBaz/enforce):

```bash
pip install typeguard
```

**Example:**

```python
from typeguard import typechecked

@typechecked
def add(x: int, y: int) -> int:
    return x + y

add("a", "b")  # Raises TypeError at runtime!
```

* * *

## 7. Best Practices for Strict Typing

* **Annotate all functions and class members.**
    
* Use modern typing features: `Optional`, `Union`, `TypedDict`, `Protocol`, etc.
    
* Run `mypy` regularly or integrate into your CI/CD.
    
* Document your typing conventions for contributors.
    
* Prefer static enforcement, and use runtime checking only for critical paths.
    

* * *

## 8. Limitations

* **Python’s type system is optional and opt-in.**
    
* Type hints are ignored by the Python interpreter by default.
    
* Some dynamic patterns can escape type checkers.
    

* * *

## Conclusion

While you can’t turn Python into Java or C#, you can come close to strict typing by embracing type hints, using mypy in strict mode, and enforcing checks with automated tools. This dramatically reduces bugs and makes your codebase more maintainable—without sacrificing Python’s expressive power.