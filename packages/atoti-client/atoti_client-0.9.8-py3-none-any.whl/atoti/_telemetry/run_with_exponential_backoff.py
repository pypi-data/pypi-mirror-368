from collections.abc import Callable, Generator
from datetime import timedelta
from threading import Event, Thread

_DEFAULT_BACKOFF_BASE = 2
_DEFAULT_FIRST_WAIT_DURATION = timedelta(seconds=1)


def _back_off_exponentially(
    *,
    base: float = _DEFAULT_BACKOFF_BASE,
) -> Generator[float, None, None]:
    step = 0
    while True:
        yield base**step
        step += 1


def run_with_exponential_backoff(
    callback: Callable[[], None],
    /,
    *,
    base: float = _DEFAULT_BACKOFF_BASE,
    daemon: bool | None = None,
    first_wait_duration: timedelta = _DEFAULT_FIRST_WAIT_DURATION,
) -> Callable[[], None]:
    scale = first_wait_duration.total_seconds()
    wait_duration_generator = _back_off_exponentially(base=base)

    stopped = Event()

    def loop() -> None:
        while not stopped.wait(scale * next(wait_duration_generator)):
            callback()

    Thread(target=loop, daemon=daemon).start()

    return stopped.set
