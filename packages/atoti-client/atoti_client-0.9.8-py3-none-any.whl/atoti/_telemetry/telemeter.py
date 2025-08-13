from __future__ import annotations

import os
from collections.abc import Callable
from typing import TypeVar

from _atoti_core import LICENSE_KEY_ENV_VAR_NAME
from typing_extensions import ParamSpec

from .._env import get_env_flag
from .import_event import ImportEvent
from .send_event import send_event
from .send_heartbeat import send_heartbeat
from .track_calls import create_decorator

_DISABLE_TELEMETRY_ENV_VAR_NAME = "_ATOTI_DISABLE_TELEMETRY"


_P = ParamSpec("_P")
_R = TypeVar("_R")


def telemeter() -> Callable[[Callable[_P, _R]], Callable[_P, _R]] | None:
    if LICENSE_KEY_ENV_VAR_NAME in os.environ or get_env_flag(
        _DISABLE_TELEMETRY_ENV_VAR_NAME,
    ):
        return None

    send_event(ImportEvent())
    send_heartbeat()
    return create_decorator()
