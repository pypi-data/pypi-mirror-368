# src/obk/application/prompts/queries/list_prompts.py
from __future__ import annotations

from dataclasses import dataclass

from obk.application.prompts.ports import PromptRepository
from obk.domain.prompts import Prompt
from obk.infrastructure.mediator.core import Query


@dataclass(frozen=True)
class ListPrompts(Query):
    pass


def handle(_: ListPrompts, repo: PromptRepository) -> list[Prompt]:
    return repo.list()
