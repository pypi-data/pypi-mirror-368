from __future__ import annotations

from datetime import timedelta
from typing import Annotated

from pydantic import AfterValidator


def _check_positive(duration: timedelta) -> Duration:
    if duration.days < 0:
        raise ValueError("A duration cannot be negative.")

    return duration


Duration = Annotated[timedelta, AfterValidator(_check_positive)]
