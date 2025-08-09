# **How to Use MediatR in Python**

As Python applications grow in complexity, developers often seek clean, testable ways to structure business logic. If you come from a .NET background, you might be familiar with **MediatR** — a popular library that enables **CQRS-style command and query dispatching** via the mediator pattern. While Python doesn’t have an official MediatR port, you can still adopt the **same architectural benefits** using lightweight libraries or by rolling your own.

This guide explains how to use MediatR-style architecture in Python, when to use it, and why it fits well in modern CLI applications.

* * *

## 🧠 What Is MediatR?

MediatR (originally for .NET) implements the **Mediator pattern**, where requests (commands or queries) are sent through a central dispatcher that finds and invokes the appropriate handler.

This results in:

* Thin orchestration layers (e.g. CLI, API)
    
* Decoupled business logic
    
* Clean command/query separation
    
* Testable, modular code
    

* * *

## 🛠️ Is There MediatR for Python?

There’s no official port by MediatR’s original creator, but several lightweight libraries implement similar behavior:

### ✅ 1. [`mediatr`](https://pypi.org/project/mediatr/)

Python’s closest analog to .NET MediatR. You register handlers for commands or queries, and send them via the mediator.

```python
from mediatr import Mediator, Request, RequestHandler

class GreetRequest(Request):
    def __init__(self, name: str):
        self.name = name

class GreetHandler(RequestHandler):
    def handle(self, request: GreetRequest):
        return f"Hello, {request.name}!"

mediator = Mediator()
mediator.register(GreetRequest, GreetHandler)
print(mediator.send(GreetRequest("Alice")))
```

### ✅ 2. [`python-mediator`](https://github.com/marcellociceri/python-mediator)

A simple implementation of the pattern with a very small footprint.

* * *

## 🧪 When Should You Use It in Python?

| Use Case | Use MediatR? |
| --- | --- |
| You're building a CLI with Typer | ✅ Yes |
| You want CQRS-style architecture | ✅ Yes |
| You need testable, decoupled logic | ✅ Yes |
| Your app has complex workflows | ✅ Yes |
| Your CLI is just a one-off tool | ❌ Probably not |
| You don’t want extra dependencies | ❌ No |

* * *

## 🚀 Real-World Use Case: CLI + XML + SQLite

Let’s say you’re building a **Python CLI using Typer** to validate XML documents and store results in **SQLite**. This is an ideal fit for CQRS:

* `ValidateXmlCommand`: Parses and validates XML data
    
* `ImportToSqliteCommand`: Inserts extracted fields into SQLite
    
* `GetValidationErrorsQuery`: Fetches issues from the database
    

Using a MediatR-style library allows you to:

* Keep the CLI thin
    
* Move orchestration logic to handler classes
    
* Cleanly separate read (query) and write (command) concerns
    
* Make business logic easily testable in isolation
    

* * *

## ⚙️ Integrating with Typer

Here’s how you could integrate MediatR with a Typer-based CLI:

```python
import typer
from mediatr import Mediator

app = typer.Typer()
mediator = Mediator()

@app.command()
def validate(file: str):
    from commands import ValidateXmlCommand
    result = mediator.send(ValidateXmlCommand(file))
    print(result)
```

This allows Typer to serve as the **entry point**, while MediatR handles orchestration behind the scenes.

* * *

## 🧱 DIY Minimal Mediator (Optional)

Prefer not to use a third-party library? You can write a basic mediator in ~10 lines:

```python
class Mediator:
    def __init__(self):
        self._handlers = {}

    def register(self, request_type, handler):
        self._handlers[request_type] = handler

    def send(self, request):
        handler = self._handlers[type(request)]
        return handler().handle(request)
```

* * *

## ⚠️ Caution: Don’t Over-Engineer

If your CLI is simple or short-lived, MediatR might add more boilerplate than benefit. Start with a few handlers, and expand only as your application grows.

* * *

## ✅ Summary

**MediatR-style patterns are a great fit for Python apps that:**

* Use Typer for CLI entry points
    
* Have structured commands and queries (CQRS)
    
* Need scalable, testable architecture
    
* Perform complex workflows like XML validation or SQLite operations
    

**Recommended libraries:**

* [`mediatr`](https://pypi.org/project/mediatr/)
    
* [`python-mediator`](https://github.com/marcellociceri/python-mediator)
    

Whether you use a third-party library or build your own, bringing MediatR-style orchestration to Python can significantly improve code structure in larger CLI applications.

* * *
