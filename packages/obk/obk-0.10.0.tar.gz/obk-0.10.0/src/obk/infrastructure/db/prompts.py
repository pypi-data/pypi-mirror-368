# src/obk/infrastructure/db/prompts.py
from __future__ import annotations

from obk.application.prompts.ports import PromptRepository
from obk.domain.prompts import Prompt


class InMemoryPromptRepository(PromptRepository):
    def __init__(self) -> None:
        self._items: list[Prompt] = []

    def add(self, prompt: Prompt) -> None:
        self._items.append(prompt)

    def list(self) -> list[Prompt]:
        return list(self._items)
