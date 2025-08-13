from io import TextIOBase
from pathlib import Path
from typing import Annotated, TextIO, final

from pydantic import PlainSerializer
from pydantic.dataclasses import dataclass

from .._pydantic import PYDANTIC_CONFIG as _PYDANTIC_CONFIG


@final
@dataclass(config=_PYDANTIC_CONFIG, frozen=True, kw_only=True)
class LoggingConfig:
    """The config describing how the session logs will be handled.

    Example:
        To stream the session logs to the Python process' standard output:

        >>> import sys
        >>> config = tt.LoggingConfig(destination=sys.stdout)

    """

    destination: (
        Annotated[
            Path | TextIO | TextIOBase,
            PlainSerializer(
                lambda destination: None
                if isinstance(destination, TextIO | TextIOBase)
                else destination,
            ),
        ]
        | None
    ) = None
    """The place where the session logs will be written to.

    If ``None``, the logs will be written to ``logs/server.log`` in the session directory under ``$ATOTI_HOME`` (this environment variable itself defaults to ``$HOME/.atoti``).

    Note:
        Unless an instance of :class:`io.TextIOBase` is passed, the rolling policy is:

        * Maximum file size of 10MB.
        * Maximum history of 7 days.

        Once the maximum size is reached, logs are archived following the pattern ``f"{destination}.{date}.{i}.gz"`` where ``date`` is the creation date of the file in the ``yyyy-MM-dd`` format and ``i`` an integer incremented during the day.

    """
