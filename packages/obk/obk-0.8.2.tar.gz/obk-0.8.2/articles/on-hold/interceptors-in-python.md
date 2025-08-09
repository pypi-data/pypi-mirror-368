# How to Mimic Interceptors in Python Using Decorators and Middleware

_Apply cross-cutting concerns to your CLI commands the Pythonic way._

* * *

## Introduction

In languages like Java and .NET, "interceptors" and "middleware" are powerful tools for handling cross-cutting concerns such as logging, authentication, and error handling. But what if you’re building a **CLI app in Python** and want to add similar functionality—without bloating your command logic? The answer: **decorators** and CLI hooks.

In this article, we’ll explore how to achieve interceptor-like behavior in a Python CLI app using modern, idiomatic techniques. You’ll see how to wrap commands for logging, validation, error handling, and more—just like middleware or interceptors in other stacks.

* * *

## What Are Interceptors (and Why Should I Care)?

**Interceptors** allow you to “intercept” the execution of a function or command—adding logic before, after, or around it—without modifying the core code.  
Common use-cases:

* Logging every command or action
    
* Authentication and authorization
    
* Consistent error handling
    
* Argument validation
    
* Analytics or metrics
    

These are also called **cross-cutting concerns**, and they keep your code DRY and maintainable.

* * *

## Pythonic Patterns: Decorators & Middleware

Python’s **decorators** are a natural fit for this purpose—they let you wrap any function (including CLI commands) with extra logic.  
CLI frameworks like **Typer** or **Click** add additional hooks for “global” middleware-like logic.

* * *

## Example: Building a CLI with Interceptor-like Features

Let’s build a sample CLI with Typer (but the patterns work with Click, too).

First, install Typer if you need:

```sh
pip install typer[all]
```

### 1. Create a Decorator for Logging (Interceptor Style)

```python
import typer
from functools import wraps

def log_command(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        command_name = func.__name__
        print(f"[LOG] Executing command: {command_name}")
        return func(*args, **kwargs)
    return wrapper
```

* * *

### 2. Apply the Decorator to Your CLI Commands

```python
app = typer.Typer()

@app.command()
@log_command
def hello(name: str):
    """Say hello."""
    print(f"Hello, {name}!")

@app.command()
@log_command
def goodbye(name: str):
    """Say goodbye."""
    print(f"Goodbye, {name}!")
```

Now, whenever you run a command, it’s “intercepted” by `log_command`:

```
$ python mycli.py hello Alice
[LOG] Executing command: hello
Hello, Alice!
```

* * *

### 3. Handling Errors and More (Multiple Interceptors)

You can stack decorators, just like chaining interceptors/middleware:

```python
def catch_errors(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(f"[ERROR] {e}")
    return wrapper

@app.command()
@catch_errors
@log_command
def risky(name: str):
    """A command that may fail."""
    if name == "fail":
        raise ValueError("Simulated failure!")
    print(f"Safe for {name}")
```

* * *

### 4. Global Middleware: Typer Callback Example

To run code before _every_ command (like global middleware), use a Typer callback:

```python
@app.callback()
def main(ctx: typer.Context):
    print("[GLOBAL] CLI app started.")
```

* * *

### 5. Dependency Injection for Advanced Scenarios

Typer supports dependency injection for commands. You can inject a logger, configuration, or authentication context, mimicking advanced interceptor patterns.

```python
def get_logger():
    def logger(msg):
        print(f"[LOG] {msg}")
    return logger

@app.command()
def whoami(logger=typer.Depends(get_logger)):
    logger("whoami command called")
    print("You are a CLI user!")
```

* * *

## Recap: Key Takeaways

* **Decorators** = function-level interceptors in Python.
    
* **Typer/Click callbacks** = global middleware for CLI apps.
    
* You can **chain decorators** for multiple cross-cutting concerns (logging, errors, validation, etc.).
    
* All these patterns keep your CLI code DRY, testable, and clean.
    

* * *

## Conclusion

While Python doesn’t have a built-in “interceptor” feature, its flexible function decorators and CLI framework hooks provide everything you need to mimic interceptors and middleware—_the Pythonic way_.  
With just a few lines, you can modularize logging, error handling, and more, making your CLI apps as robust and maintainable as any enterprise framework.

* * *

**Try these patterns in your next CLI tool and enjoy clean, reusable, cross-cutting logic—without the Java overhead.**

* * *
