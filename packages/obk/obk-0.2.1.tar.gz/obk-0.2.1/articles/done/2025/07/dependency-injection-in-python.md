
# Guide: How to Set Up Dependency Injection in Python with `dependency-injector`

**Dependency injection** is a powerful design pattern that improves modularity, testability, and maintainability—especially as projects grow. Python’s `dependency-injector` library is the most popular and feature-rich way to bring this pattern to your codebase.

* * *

## 1. **Why Use Dependency Injection in Python?**

* **Cleaner code:** Separate configuration from logic, minimize global state.
    
* **Easier testing:** Swap real implementations for mocks or stubs in tests.
    
* **Scalable architecture:** Manage growing complexity in apps, APIs, and CLIs.
    

* * *

## 2. **Install the Library**

Add to your project (usually as a development dependency):

```bash
pip install dependency-injector
```

* * *

## 3. **Key Concepts**

* **Containers:** Organize and wire your app’s dependencies.
    
* **Providers:** Define how instances are created (singleton, factory, etc.).
    
* **Wiring:** Inject dependencies into classes or functions automatically.
    

* * *

## 4. **Basic Usage Example**

Let’s see how you’d use `dependency-injector` in a simple CLI tool.

### **A. Define Your Services**

```python
# services.py

class GreetingService:
    def greet(self, name: str) -> str:
        return f"Hello, {name}!"
```

* * *

### **B. Create a Container for Dependencies**

```python
# containers.py

from dependency_injector import containers, providers
from services import GreetingService

class Container(containers.DeclarativeContainer):
    greeting_service = providers.Singleton(GreetingService)
```

* * *

### **C. Wire Up Your CLI**

```python
# main.py

from containers import Container
import click

@click.command()
@click.option('--name', default='world', help='Name to greet')
def main(name):
    container = Container()
    greeter = container.greeting_service()
    click.echo(greeter.greet(name))

if __name__ == '__main__':
    main()
```

* Here, the CLI handler gets its dependencies (the service) via the container.
    
* This is scalable to many services, config objects, and complex dependency graphs.
    

* * *

## 5. **Expanding with Configuration**

You can inject configuration from files or environment variables:

```python
class Container(containers.DeclarativeContainer):
    config = providers.Configuration()
    greeting_service = providers.Singleton(GreetingService)
```

Set config values before using the container:

```python
container = Container()
container.config.name.from_env('GREETING_NAME', default='world')
greeter = container.greeting_service()
```

* * *

## 6. **Testing with Dependency Injection**

Swap real implementations for mocks during testing:

```python
class MockGreetingService:
    def greet(self, name):
        return f"[TEST] Hi, {name}"

def test_greeting():
    from containers import Container
    container = Container()
    container.greeting_service.override(MockGreetingService())
    greeter = container.greeting_service()
    assert greeter.greet("Alice") == "[TEST] Hi, Alice"
```

* * *

## 7. **Advanced Features**

* **Asynchronous providers:** Use `providers.AsyncSingleton`, `providers.Coroutine`, etc. for async/await patterns.
    
* **Resource providers:** For things like database connections that need cleanup.
    
* **Wiring decorator:** Automatically inject dependencies into classes/functions/modules.
    

See the official docs for more on advanced usage.

* * *

## 8. **Best Practices**

* **Organize by feature:** Group related services and providers in modules.
    
* **Keep containers in a separate file:** Makes testing and wiring easier.
    
* **Avoid global state:** Always fetch dependencies from the container, not as global variables.
    
* **Leverage overrides for tests:** Easily inject fakes or mocks.
    

* * *

## 9. **Summary**

* Install `dependency-injector`
    
* Define your services and providers
    
* Organize them in containers
    
* Inject dependencies in your CLI, API, or application code
    
* Swap implementations easily for testing and scaling
    

* * *
