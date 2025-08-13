from base64 import b64encode
from collections.abc import Mapping
from dataclasses import KW_ONLY
from typing import final

from pydantic.dataclasses import dataclass
from typing_extensions import override

from .._identification import UserName
from .._pydantic import PYDANTIC_CONFIG as _PYDANTIC_CONFIG
from .authenticate import Authenticate
from .token_authentication import TokenAuthentication


@final
@dataclass(config=_PYDANTIC_CONFIG, frozen=True)
class BasicAuthentication(Authenticate):
    """Authenticate requests with `basic authentication <https://en.wikipedia.org/wiki/Basic_access_authentication>`__.

    See Also:
        :class:`atoti.BasicAuthenticationConfig`.
    """

    username: UserName
    password: str
    _: KW_ONLY

    @override
    def __call__(self, url: str) -> Mapping[str, str]:
        return self._token_authentication(url)

    @property
    def _token_authentication(self) -> TokenAuthentication:
        plain_credentials = f"{self.username}:{self.password}"
        token = str(b64encode(plain_credentials.encode("ascii")), "utf8")
        return TokenAuthentication(
            token,
            token_type="Basic",  # noqa: S106
        )
