from collections.abc import Mapping
from dataclasses import KW_ONLY
from typing import final

from pydantic.dataclasses import dataclass
from typing_extensions import override

from .._pydantic import PYDANTIC_CONFIG as _PYDANTIC_CONFIG
from .authenticate import Authenticate


@final
@dataclass(config=_PYDANTIC_CONFIG, frozen=True)
class TokenAuthentication(Authenticate):
    """Authenticate requests by passing the given token in the :guilabel:`Authorization` header.

    This is also called "Bearer authentication".
    """

    token: str
    _: KW_ONLY
    token_type: str = "Bearer"  # noqa: S105

    @override
    def __call__(
        self,
        url: str,
    ) -> Mapping[str, str]:
        return self._headers

    @property
    def _headers(self) -> Mapping[str, str]:
        return {"Authorization": f"{self.token_type} {self.token}"}
