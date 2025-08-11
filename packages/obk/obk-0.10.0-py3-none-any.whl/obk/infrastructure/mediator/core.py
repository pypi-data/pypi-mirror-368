# src/obk/infrastructure/mediator/core.py
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Protocol, TypeVar

Req = TypeVar("Req", bound="Request")


class Behavior(Protocol):
    def wrap(self, next_: Callable[[Req], object]) -> Callable[[Req], object]: ...


@dataclass(frozen=True)
class Request: ...


@dataclass(frozen=True)
class Command(Request): ...


@dataclass(frozen=True)
class Query(Request): ...


Handler = Callable[[Request], object]


class Mediator:
    """Dispatch requests to handlers with optional behaviors."""

    def __init__(
        self,
        handlers: dict[type, Handler],
        behaviors: list[Behavior] | None = None,
    ) -> None:
        self._handlers = handlers
        self._behaviors = list(behaviors or [])

    def send(self, request: Request) -> object:
        req_type = type(request)
        if req_type not in self._handlers:
            raise KeyError(f"No handler registered for {req_type.__name__}")

        def invoke(req: Request) -> object:
            return self._handlers[req_type](req)

        fn: Callable[[Request], object] = invoke
        for behavior in reversed(self._behaviors):
            fn = behavior.wrap(fn)
        return fn(request)


class LoggingBehavior:
    def __init__(self, logger: Callable[[str], None]) -> None:
        self._log = logger

    def wrap(self, next_: Callable[[Request], object]) -> Callable[[Request], object]:
        def _wrapped(req: Request) -> object:
            self._log(f"[Mediator] Handling {type(req).__name__}")
            result = next_(req)
            self._log(f"[Mediator] Handled {type(req).__name__}")
            return result

        return _wrapped
