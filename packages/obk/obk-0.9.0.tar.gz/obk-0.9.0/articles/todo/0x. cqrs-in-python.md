# **Building a Clean CQRS Architecture in Python with MediatR, sqlite-utils, and Dependency Injection**

## Introduction

If you're building a scalable Python application and want to apply **CQRS**, the **Mediator Pattern**, and **Dependency Injection**, you're already embracing clean architecture principles. But to take that even further, consider organizing your code into **Vertical Slices**.

This article walks you through implementing:

* ✅ CQRS (Command Query Responsibility Segregation)
    
* ✅ MediatR-style message dispatch
    
* ✅ sqlite-utils for clean, fast SQL-based persistence
    
* ✅ POPOs (Plain Old Python Objects) via `dataclass`
    
* ✅ Dependency Injection for testability
    
* ✅ Vertical Slice Architecture for modularity and clarity
    

* * *

## 🔹 What is Vertical Slice Architecture?

Instead of organizing code by layer (e.g. `services/`, `repositories/`, `handlers/`), you organize it **by feature**.

Each feature or use case (a "slice") contains **everything it needs** — data models, commands/queries, handlers, and tests — in one folder.

### Traditional (layered) structure:

```
handlers/
models/
repositories/
```

### Vertical Slice structure:

```
features/
├── get_active_users/
│   ├── handler.py
│   ├── query.py
│   ├── model.py
│   └── test_handler.py
```

This improves cohesion and makes the code easier to reason about and modify in isolation.

* * *

## ✅ Folder Structure (Vertical Slice Style)

```
/app
├── db/
│   └── database.py
├── features/
│   └── get_active_users/
│       ├── model.py           # POPOs / DTOs
│       ├── query.py           # Query object
│       ├── handler.py         # Query handler
│       └── test_handler.py    # Unit test
├── mediator/
│   └── registry.py
├── main.py
```

* * *

## 1. Define the Data Model (POPO)

```python
# features/get_active_users/model.py
from dataclasses import dataclass

@dataclass
class UserDto:
    id: int
    name: str
    active: bool
```

* * *

## 2. Define the Query DTO

```python
# features/get_active_users/query.py
class GetActiveUsersQuery:
    pass
```

* * *

## 3. Create the Query Handler

```python
# features/get_active_users/handler.py
from sqlite_utils import Database
from .model import UserDto
from .query import GetActiveUsersQuery

class GetActiveUsersHandler:
    def __init__(self, db: Database):
        self.db = db

    def handle(self, query: GetActiveUsersQuery) -> list[UserDto]:
        rows = self.db["users"].rows_where("active = 1")
        return [UserDto(**row) for row in rows]
```

* * *

## 4. Register the Handler in MediatR

```python
# mediator/registry.py
from mediatr import Mediator
from db.database import provide_database
from features.get_active_users.query import GetActiveUsersQuery
from features.get_active_users.handler import GetActiveUsersHandler

def build_mediator() -> Mediator:
    mediator = Mediator()
    db = provide_database()
    handler = GetActiveUsersHandler(db)
    mediator.register(GetActiveUsersQuery, handler.handle)
    return mediator
```

* * *

## 5. Compose and Execute in `main.py`

```python
# main.py
from mediator.registry import build_mediator
from features.get_active_users.query import GetActiveUsersQuery

mediator = build_mediator()
users = mediator.send(GetActiveUsersQuery())

for user in users:
    print(user.name)
```

* * *

## 6. Test the Handler in Isolation

```python
# features/get_active_users/test_handler.py
from sqlite_utils import Database
from .handler import GetActiveUsersHandler
from .query import GetActiveUsersQuery

def test_get_active_users_handler():
    db = Database(memory=True)
    db["users"].insert_all([
        {"id": 1, "name": "Alice", "active": 1},
        {"id": 2, "name": "Bob", "active": 0},
    ])

    handler = GetActiveUsersHandler(db)
    result = handler.handle(GetActiveUsersQuery())

    assert len(result) == 1
    assert result[0].name == "Alice"
```

* * *

## ✅ Benefits of Vertical Slice Architecture

| Benefit | Why It Matters |
| --- | --- |
| 📦 Feature modularity | Each slice is self-contained and easy to understand |
| 🔄 Scalability | Easy to add new features without touching global files |
| 🧪 Testability | Unit tests live alongside the logic they test |
| 🧘 Cleaner mental model | You focus on _features_, not _layers_ |

* * *

## Summary

Using Vertical Slice Architecture, you've now built a **modular, testable CQRS application** in Python using:

* ✅ `sqlite-utils` for raw SQL and dict-based rows
    
* ✅ `@dataclass` POPOs for DTOs
    
* ✅ `mediatr` for message dispatching
    
* ✅ DI for composability and testing
    
* ✅ Vertical Slices for feature-driven structure
    

This approach works extremely well for CLI tools, backend APIs, or data transformation pipelines — and is particularly effective when paired with Codex or automation systems that operate on a per-feature basis.
