# Refactoring Your Python CLI: From Functions to Classes

## Why Convert a Simple CLI to Class-Based?

Even a basic CLI (“hello world!”) works fine with a few functions. But if you expect your project to:

* Grow with more commands or options,
    
* Need configuration, logging, or reusable logic,
    
* Require easier unit testing or dependency injection…
    

...**it pays off to organize your CLI around classes.**

### Benefits:

* **Encapsulation:** Related logic and state live together.
    
* **Extensibility:** Add new features without global sprawl.
    
* **Testability:** Swap implementations or mock dependencies in tests.
    
* **Clarity:** Clear separation of concerns as your CLI grows.
    

* * *

## 1. The Starting Point: Function-Based Hello World

Here’s a typical function-based CLI using Click:

```python
import click

@click.command()
@click.option('--name', default='world')
def hello(name):
    click.echo(f"Hello, {name}!")

if __name__ == '__main__':
    hello()
```

* * *

## 2. The Class-Based Approach

We’ll refactor this so all logic is encapsulated in a class.

### **A. Define a Greeter Class**

```python
class Greeter:
    def greet(self, name: str) -> str:
        return f"Hello, {name}!"
```

### **B. Update the CLI to Use the Class**

```python
import click
from greeter import Greeter  # Assuming you split it into a file, optional

@click.command()
@click.option('--name', default='world')
def hello(name):
    greeter = Greeter()
    click.echo(greeter.greet(name))

if __name__ == '__main__':
    hello()
```

* * *

## 3. Scaling Up (Add More Commands or Services)

Once you have logic in classes, you can:

* Add configuration or dependencies in the constructor
    
* Easily test with mock objects
    
* Use dependency injection for advanced setups
    

**Example with Multiple Commands:**

```python
import click

class Greeter:
    def greet(self, name):
        return f"Hello, {name}!"

    def farewell(self, name):
        return f"Goodbye, {name}!"

greeter = Greeter()

@click.group()
def cli():
    pass

@cli.command()
@click.option('--name', default='world')
def hello(name):
    click.echo(greeter.greet(name))

@cli.command()
@click.option('--name', default='world')
def bye(name):
    click.echo(greeter.farewell(name))

if __name__ == '__main__':
    cli()
```

* * *

## 4. Why Use This Pattern?

* **Real-world CLI apps get complicated:** Logging, config, DB connections, etc.  
    Class-based design keeps these manageable.
    
* **It sets you up for tools like `dependency-injector`.**
    
* **It helps with testing:**  
    You can inject a mock `Greeter` for unit tests, for example.
    

* * *

## 5. Next Steps

* **Extract logic into more classes** as the app grows (e.g., `ConfigLoader`, `Logger`, etc.)
    
* **Adopt DI tools** (see our [dependency-injector guide](#) above) for maximum flexibility.
    
* **Write tests** for your classes (using `pytest` or `unittest`).
    

* * *

## Conclusion

> Even if your CLI is “just hello world,” structuring it around classes prepares you for growth, testing, and cleaner code.  
> It’s a small refactor today that saves big headaches tomorrow.