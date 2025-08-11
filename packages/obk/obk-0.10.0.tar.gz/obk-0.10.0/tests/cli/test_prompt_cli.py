from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any

from typer.testing import CliRunner

from obk.application.prompts.commands.add_prompt import AddPrompt
from obk.application.prompts.queries.list_prompts import ListPrompts
from obk.presentation.cli.prompt_cmds import build_prompt_typer


@dataclass
class FakeMediator:
    sent: list[Any]

    def send(self, msg: Any) -> Sequence[Any]:
        self.sent.append(msg)
        if isinstance(msg, ListPrompts):
            return [type("P", (), {"id": "p1", "date_utc": "2025-08-10", "type": "demo"})()]
        return []


@dataclass
class FakeContainer:
    mediator_obj: FakeMediator

    def mediator(self) -> FakeMediator:
        return self.mediator_obj


def test_prompt_cli_dispatches_via_mediator() -> None:
    med = FakeMediator([])
    app = build_prompt_typer(FakeContainer(med))
    runner = CliRunner()

    res = runner.invoke(app, ["add", "p-1", "demo", "--date", "2025-08-10"])
    assert res.exit_code == 0
    assert isinstance(med.sent[0], AddPrompt)
    assert med.sent[0].id == "p-1"
    med.sent.clear()

    res = runner.invoke(app, ["list"])
    assert res.exit_code == 0
    assert isinstance(med.sent[0], ListPrompts)
    assert "p1\t2025-08-10\tdemo" in res.stdout
