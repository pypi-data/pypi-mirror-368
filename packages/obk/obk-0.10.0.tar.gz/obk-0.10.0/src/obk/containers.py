"""Dependency injection container for the obk CLI."""
from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import cast

from dependency_injector import containers, providers

from .application.prompts.commands.add_prompt import AddPrompt
from .application.prompts.commands.add_prompt import handle as handle_add_prompt
from .application.prompts.ports import PromptRepository
from .application.prompts.queries.list_prompts import ListPrompts
from .application.prompts.queries.list_prompts import handle as handle_list_prompts
from .infrastructure.db.engine import make_engine
from .infrastructure.db.prompts import InMemoryPromptRepository
from .infrastructure.db.sqlalchemy_repo import SqlAlchemyPromptRepository
from .infrastructure.db.sqlite import SqlitePromptRepository  # optional: raw sqlite repo
from .infrastructure.mediator.core import Behavior, Handler, LoggingBehavior, Mediator
from .services import Divider, Greeter


def _build_mediator(
    repo: PromptRepository, logger: Callable[[str], None]
) -> Mediator:
    handlers: dict[type, Handler] = {
        AddPrompt: lambda req: handle_add_prompt(cast(AddPrompt, req), repo),
        ListPrompts: lambda req: handle_list_prompts(cast(ListPrompts, req), repo),
    }
    behaviors: list[Behavior] = [cast(Behavior, LoggingBehavior(logger))]
    return Mediator(handlers, behaviors)


class Container(containers.DeclarativeContainer):
    """Application container."""

    config = providers.Configuration()
    greeter = providers.Factory(Greeter)
    divider = providers.Factory(Divider)

    # Decide repo based on presence of a DB path
    _repo_key = providers.Callable(lambda p: "sqlite" if p else "memory", config.db_path)

    # Engine + repos
    engine = providers.Singleton(make_engine, db=providers.Callable(Path, config.db_path))
    
    _sqlite_repo = providers.Singleton(
    SqlitePromptRepository,
    db=providers.Callable(Path, config.db_path),
    )

    _sqlalchemy_repo = providers.Singleton(SqlAlchemyPromptRepository, engine=engine)

    # Prefer SQLAlchemy when db_path is provided; otherwise in-memory
    prompt_repository = providers.Selector(
        _repo_key,
        sqlite=_sqlalchemy_repo,
        memory=providers.Singleton(InMemoryPromptRepository),
    )

    mediator = providers.Factory(
        _build_mediator, repo=prompt_repository, logger=providers.Object(print)
    )
