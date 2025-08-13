from __future__ import annotations

from abc import ABC
from dataclasses import field
from functools import cache
from uuid import uuid4

from pydantic.dataclasses import dataclass

from .._pydantic import PYDANTIC_CONFIG


@cache
def _get_process_id() -> str:
    return str(uuid4())


@dataclass(config=PYDANTIC_CONFIG, frozen=True, kw_only=True)
class Event(ABC):
    process_id: str = field(default_factory=_get_process_id, init=False)
    event_type: str
