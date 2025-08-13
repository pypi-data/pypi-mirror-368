from typing import final

from pydantic import JsonValue
from pydantic.dataclasses import dataclass

from .._collections import FrozenMapping
from .._pydantic import PYDANTIC_CONFIG as _PYDANTIC_CONFIG


@final
@dataclass(config=_PYDANTIC_CONFIG, frozen=True, kw_only=True)
class Request:
    """The request of a custom :meth:`~atoti.Session.endpoint`."""

    url: str
    """The URL on which the client request is made."""

    path_parameters: FrozenMapping[str, str]
    """Mapping from path parameter name to parameter value in this request."""

    body: JsonValue
    """Parsed JSON body."""
