from __future__ import annotations

from collections.abc import Iterable, Sequence
from datetime import datetime
from typing import cast
from zoneinfo import ZoneInfo

import typer

from ...application.prompts.commands.add_prompt import AddPrompt
from ...application.prompts.queries.list_prompts import ListPrompts
from ...containers import Container


def _today_utc_str() -> str:
    # YYYY-MM-DD in UTC to satisfy domain expectations
    return datetime.now(ZoneInfo("UTC")).strftime("%Y-%m-%d")


def build_prompt_typer(container: Container | None = None) -> typer.Typer:
    """
    Returns a Typer app wired to send CQRS commands/queries through the mediator.
    No infra imports; strictly application-facing.
    """
    c = container or Container()
    app = typer.Typer(help="Manage prompts via CQRS handlers")

    @app.command("add")
    def add(
        id: str = typer.Argument(..., help="Prompt id"),
        type: str = typer.Argument(..., help="Prompt type"),
        date: str | None = typer.Option(None, "--date", "-d", help="UTC date YYYY-MM-DD"),
    ) -> None:
        d = date or _today_utc_str()
        c.mediator().send(AddPrompt(id=id, date_utc=d, type=type))
        typer.echo(f"Added\t{id}\t{d}\t{type}")

    @app.command("list")
    def list_() -> None:
        items = cast(
            Sequence[object],
            c.mediator().send(ListPrompts()),
        )# domain types, not enforced here
        for p in cast(Iterable[object], items):
            # duck-type: expects attributes id, date_utc, type
            _id = getattr(p, "id", "")
            _date = getattr(p, "date_utc", "")
            _type = getattr(p, "type", "")
            typer.echo(f"{_id}\t{_date}\t{_type}")

    return app

