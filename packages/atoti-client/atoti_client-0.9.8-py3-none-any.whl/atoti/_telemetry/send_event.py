from concurrent.futures import Executor, ThreadPoolExecutor
from datetime import timedelta
from functools import cache
from typing import NoReturn

import httpx

from .._env import get_env_flag
from .._pydantic import get_type_adapter
from .event import Event

_TEST_TELEMETRY_ENV_VAR_NAME = "_ATOTI_TEST_TELEMETRY"
_TIMEOUT = timedelta(seconds=5)


@cache
def _get_executor() -> Executor:
    # Sending events in the background to not bother the user.
    return ThreadPoolExecutor(max_workers=1)


def _test_request_hook(request: httpx.Request) -> NoReturn:
    assert isinstance(request.content, bytes)
    print(request.content.decode())  # noqa: T201
    raise RuntimeError("This hook cancels the request.")


@cache
def _get_http_client() -> httpx.Client:
    client = httpx.Client(
        base_url="https://telemetry.atoti.io/events",
    )

    # Branching off at the last moment to keep the test behavior as close as possible to the regular one.
    if get_env_flag(_TEST_TELEMETRY_ENV_VAR_NAME):
        client.event_hooks["request"].append(_test_request_hook)

    return client


def send_event(event: Event, /) -> None:
    body = {"events": [event]}

    executor = _get_executor()
    http_client = _get_http_client()

    def _send_event() -> None:
        content = get_type_adapter(dict).dump_json(body)
        http_client.post(
            "events",
            content=content,
            timeout=_TIMEOUT.total_seconds(),
        )

    executor.submit(_send_event)
