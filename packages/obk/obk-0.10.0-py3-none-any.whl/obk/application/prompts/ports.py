# src/obk/application/prompts/ports.py
from __future__ import annotations

from typing import Protocol

from obk.domain.prompts import Prompt


class PromptRepository(Protocol):
    def add(self, prompt: Prompt) -> None: ...
    def list(self) -> list[Prompt]: ...
