from typing import final

from pydantic.dataclasses import dataclass

from .._collections.frozen_collections import FrozenSequence
from .._pydantic import PYDANTIC_CONFIG as _PYDANTIC_CONFIG


@final
@dataclass(config=_PYDANTIC_CONFIG, frozen=True, kw_only=True)
class CorsConfig:
    """The `CORS <https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/CORS>`__ config."""

    allowed_origins: FrozenSequence[str] = ("*",)
    """The allowed origins for CORS requests.

    Allowed elements are:

    * The ``"*"`` special value for all origins.
    * A specific domain such as ``"https://example.org"``.

    """
