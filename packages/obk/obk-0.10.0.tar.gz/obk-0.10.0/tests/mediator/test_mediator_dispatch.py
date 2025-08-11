from obk.application.prompts.commands.add_prompt import AddPrompt
from obk.application.prompts.queries.list_prompts import ListPrompts
from obk.containers import Container


def test_mediator_dispatch() -> None:
    mediator = Container().mediator()
    mediator.send(AddPrompt("p1", "2025-08-10", "user"))
    items = mediator.send(ListPrompts())
    assert [p.id for p in items] == ["p1"]
