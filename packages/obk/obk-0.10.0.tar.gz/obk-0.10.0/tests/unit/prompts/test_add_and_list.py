from obk.application.prompts.commands.add_prompt import AddPrompt
from obk.application.prompts.commands.add_prompt import handle as add_handle
from obk.application.prompts.ports import PromptRepository
from obk.application.prompts.queries.list_prompts import ListPrompts
from obk.application.prompts.queries.list_prompts import handle as list_handle
from obk.domain.prompts.models import Prompt


class FakeRepo(PromptRepository):
    def __init__(self) -> None:
        self.items: list[Prompt] = []

    def add(self, p: Prompt) -> None:
        self.items.append(p)

    def list(self) -> list[Prompt]:
        return list(self.items)


def test_add_then_list() -> None:
    repo = FakeRepo()
    add_handle(AddPrompt(id="1", date_utc="2025-08-10", type="demo"), repo)
    out = list_handle(ListPrompts(), repo)
    assert out == [Prompt("1", "2025-08-10", "demo")]
