from __future__ import annotations

from collections.abc import Callable
from dataclasses import field
from datetime import timedelta
from typing import final

from pydantic.dataclasses import dataclass

from .._pydantic import PYDANTIC_CONFIG
from .event import Event
from .run_with_exponential_backoff import run_with_exponential_backoff
from .send_event import send_event


@final
@dataclass(config=PYDANTIC_CONFIG, frozen=True, kw_only=True)
class HeartbeatEvent(Event):
    """Triggered periodically to indicate that the process is still running."""

    event_type: str = field(default="heartbeat", init=False)


_FIRST_WAIT_DURATION = timedelta(seconds=30)


def send_heartbeat() -> Callable[[], None]:
    return run_with_exponential_backoff(
        lambda: send_event(HeartbeatEvent()),
        daemon=True,
        first_wait_duration=_FIRST_WAIT_DURATION,
    )
