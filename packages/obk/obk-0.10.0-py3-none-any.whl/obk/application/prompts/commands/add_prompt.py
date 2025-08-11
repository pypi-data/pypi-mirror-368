# src/obk/application/prompts/commands/add_prompt.py
from __future__ import annotations

from dataclasses import dataclass

from obk.application.prompts.ports import PromptRepository
from obk.domain.prompts import Prompt
from obk.infrastructure.mediator.core import Command


@dataclass(frozen=True)
class AddPrompt(Command):
    id: str
    date_utc: str
    type: str


def handle(req: AddPrompt, repo: PromptRepository) -> None:
    repo.add(Prompt(req.id, req.date_utc, req.type))
