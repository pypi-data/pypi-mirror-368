from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Prompt:
    """Represents a stored prompt."""

    id: str
    date_utc: str
    type: str
