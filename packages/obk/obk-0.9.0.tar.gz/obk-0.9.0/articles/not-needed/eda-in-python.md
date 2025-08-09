---

# NOT NEEDED FOR OBK. SEE Q&A AFTER ARTICLE
----------------------------------------------

# How to Implement Event‑Driven Architecture and Domain Events in Python

Event‑Driven Architecture (EDA) has become a mainstream approach for building responsive, loosely‑coupled systems that can evolve and scale independently. Python’s rich ecosystem—ranging from `asyncio` to production‑grade brokers such as Kafka and RabbitMQ—makes it an excellent language for adopting EDA both inside a single application and across a fleet of micro‑services.

This article walks through the core concepts of EDA, shows how to model **domain events**, and provides step‑by‑step Python examples that start simple (an in‑memory event bus) and graduate to fully asynchronous, broker‑backed messaging.

* * *

## 1. Why Event‑Driven Architecture?

| Challenge in traditional designs | How EDA helps |
| --- | --- |
| **Tight coupling**—callers must know about concrete implementations. | **Publish/subscribe** decouples senders from receivers. |
| **Synchronous latency**—each remote call blocks the caller. | **Asynchronous messaging** lets publishers continue immediately. |
| **Hard to scale pieces independently.** | Consumers can be scaled horizontally without changing producers. |
| **Poor change isolation**—a new feature means changing many services. | New consumers can subscribe to existing events without touching publishers. |

* * *

## 2. Key Concepts and Terminology

| Term | Definition |
| --- | --- |
| **Event** | An immutable fact describing something that _happened_ (e.g., `PaymentAuthorized`). |
| **Domain Event** | Represents a business‑meaningful occurrence _inside the bounded context_ (e.g., `OrderPlaced`). |
| **Integration Event** | Carries information _between_ bounded contexts or services. |
| **Producer** | Component that creates and publishes events. |
| **Consumer / Handler** | Component that reacts to events. |
| **Event Bus / Broker** | The conduit: in‑process (simple) or external (Kafka, RabbitMQ, Redis Streams). |

* * *

## 3. Designing Good Domain Events

1. **Name events past‑tense**—they are statements of fact (`InvoiceSent`, not `SendInvoice`).
    
2. **Include only what consumers need**, not your entire entity.
    
3. **Make them immutable**—never update an event after publication.
    
4. **Version carefully**—add new optional fields; avoid breaking old consumers.
    
5. **Prefer small, well‑defined payloads** (serializable to JSON/Avro/Protobuf).
    

* * *

## 4. In‑Process Event Bus: A Minimal Working Example

Start small—many domains flourish with an in‑memory bus before reaching for Kafka.

```python
from __future__ import annotations
from dataclasses import dataclass, asdict
from collections import defaultdict
from typing import Callable, Dict, List, Type

# ---- Domain events ----------------------------------------------------------

@dataclass(frozen=True)
class DomainEvent:
    pass

@dataclass(frozen=True)
class OrderPlaced(DomainEvent):
    order_id: str
    customer_id: str
    total: float

# ---- Event bus --------------------------------------------------------------

Handler = Callable[[DomainEvent], None]

class EventBus:
    def __init__(self) -> None:
        self._handlers: Dict[Type[DomainEvent], List[Handler]] = defaultdict(list)

    def subscribe(self, event_type: Type[DomainEvent], handler: Handler) -> None:
        self._handlers[event_type].append(handler)

    def publish(self, event: DomainEvent) -> None:
        for handler in self._handlers[type(event)]:
            handler(event)

# ---- Application service ----------------------------------------------------

class CheckoutService:
    def __init__(self, bus: EventBus) -> None:
        self.bus = bus

    def place_order(self, order_id: str, customer_id: str, total: float) -> None:
        # 1. domain logic here (e.g., reserve inventory, charge card) …
        # 2. raise domain event
        self.bus.publish(OrderPlaced(order_id, customer_id, total))

# ---- Wiring & usage ---------------------------------------------------------

def send_confirmation_email(evt: OrderPlaced) -> None:
    print(f"Email → Customer {evt.customer_id}: order {evt.order_id} confirmed.")

bus = EventBus()
bus.subscribe(OrderPlaced, send_confirmation_email)

service = CheckoutService(bus)
service.place_order("A123", "C456", 199.99)
```

_Output_

```
Email → Customer C456: order A123 confirmed.
```

### Take‑aways

* **Zero infrastructure**—great for a monolith or single process micro‑service.
    
* Still **synchronous inside** the process; you’ll offload later for full async.
    
* Use this pattern for **Domain Driven Design (DDD)** aggregates that publish events after state changes.
    

* * *

## 5. Going Asynchronous with `asyncio`

If your consumers perform I/O (e.g., HTTP calls), convert handlers to coroutines:

```python
import asyncio
from typing import Awaitable, Coroutine

AsyncHandler = Callable[[DomainEvent], Awaitable[None]]

class AsyncEventBus:
    def __init__(self) -> None:
        self._handlers: Dict[Type[DomainEvent], List[AsyncHandler]] = defaultdict(list)

    def subscribe(self, event_type: Type[DomainEvent], handler: AsyncHandler) -> None:
        self._handlers[event_type].append(handler)

    async def publish(self, event: DomainEvent) -> None:
        await asyncio.gather(*(h(event) for h in self._handlers[type(event)]))
```

Under load, this lets your CPU‑bound publisher continue while consumers await I/O.

* * *

## 6. Scaling Out: External Brokers

| Broker | Python Client | Strengths |
| --- | --- | --- |
| **RabbitMQ** | `pika`, `aio‑pika` | Simple, mature, best‑in‑class routing (topic, fan‑out, dead‑letter). |
| **Kafka** | `confluent‑kafka‑python`, `aiokafka` | Ordered partitions, huge throughput, long retention. |
| **Redis Streams** | `redis‑py` | Good for lightweight pub/sub, minimal operational overhead. |
| **AWS SQS + SNS** | `boto3` | Fully managed, easy to integrate in serverless stacks. |

### Example: Publishing to RabbitMQ with `aio‑pika`

```python
import json, asyncio, aio_pika
from pydantic import BaseModel

class OrderPlacedEvt(BaseModel):
    order_id: str
    customer_id: str
    total: float
    type: str = "OrderPlaced"   # envelope for routing/versioning

async def publish_rabbit(event: OrderPlacedEvt) -> None:
    conn = await aio_pika.connect_robust("amqp://guest:guest@rabbit/")
    async with conn:
        ch = await conn.channel()
        await ch.default_exchange.publish(
            aio_pika.Message(body=event.model_dump_json().encode()),
            routing_key="orders.events",
        )
```

Consumers bind to the `"orders.events"` routing key (topic exchange) and deserialize the JSON back into the `OrderPlacedEvt` model.

* * *

## 7. Persisting Events: Event Sourcing (When You Need It)

Storing every domain event creates a perfect audit trail and lets you rebuild an aggregate’s state **by replay**, but introduces extra complexity.

```python
from sqlalchemy import Column, String, Float, DateTime
from sqlalchemy.orm import declarative_base
import datetime, json

Base = declarative_base()

class EventRecord(Base):
    __tablename__ = "events"
    id = Column(String, primary_key=True)
    type = Column(String)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    payload = Column(String)  # JSON string

def save_event(session, evt: DomainEvent) -> None:
    session.add(EventRecord(
        id=str(uuid.uuid4()),
        type=evt.__class__.__name__,
        payload=json.dumps(asdict(evt)),
    ))
```

Choose a dedicated **Event Store DB** (EventStoreDB, Axon) if your throughput is high or you need built‑in projections.

* * *

## 8. Testing Strategies

* **Unit Tests**: Verify an aggregate publishes the correct events (assert on the in‑memory bus).
    
* **Contract Tests**: Schema‑regression tests on serialized events (Avro schema registry + CI gate).
    
* **Replay Tests**: Rehydrate aggregates from a slice of the event log and assert deterministic outcomes.
    

* * *

## 9. Observability and Operations

1. **Structured logging**—include correlation IDs in both HTTP calls and events.
    
2. **Tracing**—tools like OpenTelemetry can join publish and consume spans.
    
3. **Dead‑Letter Queues**—always configure for poison messages.
    
4. **Metrics**—publish lag, consumer errors, retry counts; alert early.
    

* * *

## 10. Common Pitfalls

| Pitfall | Prevention |
| --- | --- |
| **Chatty events**—firing on every property change. | Emit events at meaningful business boundaries. |
| **Leaking private entities** into event payloads. | Use purpose‑built DTOs; never serialize active records. |
| **Tight coupling via schemas**—consumers break on field addition. | Evolve schemas compatibly; mark new fields optional. |
| **“Last‑write‑wins” updates** across multiple consumers. | Use idempotent handlers and deduplicate by event ID. |

* * *

## 11. Putting It All Together

1. **Start in‑process**—publish domain events from aggregates into an internal bus.
    
2. **Extract asynchronous consumers** when work becomes slow or independent.
    
3. **Introduce a broker** only when crossing process boundaries or scaling horizontally.
    
4. **Persist events** for audit trails or when you need to rebuild state (event sourcing).
    
5. **Automate contracts, monitoring, and retries** from the outset—operational polish pays off.
    

* * *

## 12. Further Reading

* _Domain‑Driven Design: Tackling Complexity in the Heart of Software_ — Eric Evans
    
* _Building Event‑Driven Microservices_ — Adam Bellemare
    
* Martin Fowler’s essay “What Do You Mean by ‘Event‑Driven’?”
    
* Saga, Outbox, and Transactional Messaging patterns (Microsoft e‑book **Cloud Design Patterns**)
    

* * *

**Conclusion**

Implementing Event‑Driven Architecture and domain events in Python is a journey of progressive decoupling. Begin with clear, immutable domain events and an in‑memory bus. As your needs outgrow a single process, reach for asynchronous brokers like RabbitMQ or Kafka, and treat infrastructure concerns—retries, idempotency, observability—as first‑class citizens. With disciplined event design and Python’s vibrant toolkit, you can build systems that are not only scalable and resilient, but also reflect the language of your business.

## **Q&A: Should OBK Adopt Event-Driven Architecture (EDA)?**

### **Q: Can an Event-Driven Architecture (EDA) be implemented in a CLI like OBK?**

**A:**  
Yes. There’s nothing technically preventing OBK (or any Python CLI) from implementing EDA patterns. You could wire up an in-process event bus, or even emit events to external brokers (like RabbitMQ or Kafka) if the CLI needs to orchestrate other systems or processes. The EDA article demonstrates both in-memory and async event buses, and these could be adapted for OBK if needed.

* * *

### **Q: Is EDA a good fit for OBK’s current and future architecture?**

**A:**  
Not right now, and likely not for the foreseeable future—unless OBK evolves into a complex orchestrator of asynchronous workflows or external services.

* **OBK is a CLI:** Each invocation is short-lived and synchronous. Most commands perform local actions, print results, and exit.
    
* **Dependency injection is already used:** OBK uses a DI container to manage and decouple services (like `Greeter`, `Divider`). This pattern already provides the core modularity and testability needed for scalable CLI development.
    
* **Commands are modular and testable:** Each command can be developed, tested, and extended without EDA overhead.
    
* **Typer (or argparse) provides extensibility:** With frameworks like Typer, it’s straightforward to add and organize subcommands. Typer also makes it easy to inject dependencies and scale up the CLI structure as new commands are added.
    
* **EDA adds complexity:** Introducing EDA (event schemas, bus management, async handling, brokers) is only justified if you have a concrete need for decoupling _across_ plugins, long-running background tasks, or distributed service orchestration. For OBK’s current model, this is premature.
    

* * *

### **Q: Is EDA common in Python CLI applications?**

**A:**  
No, not for tools like OBK.  
Event-driven design is prevalent in servers, microservices, and some plugin-heavy frameworks, but almost never in CLI tools that run, complete a task, and exit. Big CLIs (like git, kubectl, poetry) use plugin hooks or command dispatch, but don’t wire up event brokers or publish/subscribe systems internally. Most use modular design and, at most, simple hooks for extensibility.

* * *

### **Q: What’s the best way for OBK to remain scalable and maintainable as the number of commands grows?**

**A:**

* **Stick with dependency injection:** Continue using DI to keep command logic and services loosely coupled and easy to test.
    
* **Consider Typer for rapid scaling:** If you’re not already using it, Typer is designed for scalable, maintainable CLI apps—automatic help, subcommand registration, type hints, and easy integration with your DI pattern.
    
* **Focus on code quality:** Maintain high test coverage, address linter/formatter warnings (`black`, `ruff`), and prune unused dependencies.
    
* **Plugins before EDA:** If you need to support third-party extensions or internal plugins, consider a plugin registry or loading pattern before reaching for event buses.
    
* **Add EDA _only_ if you need async orchestration:** If OBK ever needs to trigger long-running, cross-system workflows (background jobs, microservice coordination), follow the EDA article’s progression: start with a simple in-memory event bus, and reach for async or broker-backed solutions only when absolutely necessary.
    

* * *

### **Q: Are there any code or architecture changes needed now?**

**A:**

* **Clean up dependencies:** If `typer[all]` is declared but not used, remove it to slim the package.
    
* **Keep up with formatting/linting:** Run `black` and fix `ruff` warnings to maintain code quality.
    
* **Maintain testing discipline:** Current subprocess-based CLI tests are good for validating behavior from the entry point. Keep test coverage high as new commands are added.
    

* * *

### **Summary**

> **OBK already uses modern, scalable patterns (DI, modular commands, good testing). For 99% of CLI use cases—including large, extensible tools—this is enough. Only add event-driven architecture if you face a real need for asynchronous workflows or cross-process orchestration. Until then, keep it simple and focused.**