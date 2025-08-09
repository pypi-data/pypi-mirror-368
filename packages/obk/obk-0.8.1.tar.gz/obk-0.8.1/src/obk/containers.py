"""Dependency injection container for the obk CLI."""

from __future__ import annotations

from dependency_injector import containers, providers

from .services import Divider, Greeter


class Container(containers.DeclarativeContainer):
    """Application container."""

    config = providers.Configuration()
    greeter = providers.Factory(Greeter)
    divider = providers.Factory(Divider)
