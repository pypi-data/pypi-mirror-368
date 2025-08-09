# Clean-on-Top, Slice-in-Below Structure in Python

## Introduction

Python doesn’t have DLLs, project files, or enforced module boundaries like .NET—but that doesn’t mean we can’t have architectural discipline. By combining the rigor of **Clean Architecture** with the modularity of **Vertical Slice Architecture**, we can scale Python applications with clear boundaries, localized changes, and high testability.

This hybrid approach—**Clean-on-Top, Slice-in-Below**—offers the best of both worlds.

* * *

## What Is Clean-on-Top, Slice-in-Below?

In traditional Clean Architecture, the project is divided by _layers_:

* `domain/` – core business logic
    
* `application/` – use cases and orchestrators
    
* `infrastructure/` – implementation details (DB, I/O)
    
* `cli/` – UI or interface layer (e.g. Typer-based CLI)
    

Vertical Slice Architecture, on the other hand, organizes code by _feature_ rather than by type. Each feature has its own logic, data, UI, and tests grouped together.

**Clean-on-Top, Slice-in-Below** combines both:

* **Top-level folders are Clean Architecture layers**
    
* **Within each layer, code is organized into vertical slices (by feature)**
    

* * *

## Folder Layout

Here’s what it looks like in practice:

```
obk/
├── domain/
│   ├── greet/
│   │   └── greeter.py
│   └── divide/
│       └── divider.py
├── application/
│   ├── greet/
│   │   └── use_case.py
│   └── divide/
│       └── use_case.py
├── infrastructure/
│   ├── greet/
│   │   └── sqlite_repo.py
│   └── divide/
│       └── sqlite_repo.py
├── cli/
│   ├── greet.py
│   └── divide.py
├── container.py
└── pyproject.toml
```

Each feature has its own subfolder _within each layer_. That makes it easy to:

* Enforce clean architectural boundaries
    
* Keep all logic related to a feature discoverable
    
* Scale without sacrificing clarity
    

* * *

## Dependency Flow

Dependencies must respect Clean Architecture:

* `cli → application → domain`
    
* `infrastructure → domain`
    
* `domain` knows nothing about anything else
    

To enforce this in Python (which doesn’t do this natively), you can use:

* `import-linter` to prevent violations
    
* `dependency-injector` to wire dependencies between layers without tight coupling
    

* * *

## Example: `greet` Feature

```
domain/greet/greeter.py
application/greet/use_case.py
infrastructure/greet/sqlite_repo.py
cli/greet.py
```

In this slice:

* `greeter.py` defines the core logic or interface
    
* `use_case.py` orchestrates the interaction
    
* `sqlite_repo.py` implements the storage
    
* `greet.py` exposes the feature to the CLI
    

Each slice is self-contained but layered cleanly.

* * *

## Benefits

| Feature | Why it matters |
| --- | --- |
| 🔒 Enforced boundaries | Clean separation of concerns; DI and interface-driven |
| 🧩 Slice modularity | Easy to add, remove, or rewrite a feature |
| 🧪 Testability | Slices are independently testable and mockable |
| 🧠 Developer clarity | Easy to find logic: it's grouped by feature but still layered |
| 🧱 Scale-friendly | Structure holds up as the codebase grows |

* * *

## Enforcing the Structure

### Linting with `import-linter`

You can write rules like:

```ini
[contract: clean-arch]
type = layered
layers =
    cli
    application
    domain
    infrastructure
containers =
    obk.cli
    obk.application
    obk.domain
    obk.infrastructure
```

Or define slice-specific contracts:

```ini
[contract: greet-slice]
type = layered
layers =
    cli
    application
    domain
    infrastructure
containers =
    obk.cli.greet
    obk.application.greet
    obk.domain.greet
    obk.infrastructure.greet
```

### Dependency Injection

Use dependency-injector to wire dependencies slice-by-slice. Keep wiring logic in `container.py` and avoid implicit coupling between layers.

* * *

## Conclusion

The **Clean-on-Top, Slice-in-Below** structure brings order to complexity. It makes Python applications:

* Easier to reason about
    
* Easier to test
    
* Easier to scale
    

You don’t need DLLs or static analyzers built into the language—you just need **intentional structure**. With the right tooling and discipline, Python can support modern architecture patterns as cleanly as any compiled language.

* * *