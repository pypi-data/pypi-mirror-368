from collections.abc import Mapping, Set as AbstractSet
from functools import cache, cached_property
from typing import final
from urllib.parse import urljoin

import httpx
from pydantic.dataclasses import dataclass
from typing_extensions import TypedDict, override

from .._pydantic import PYDANTIC_CONFIG as _PYDANTIC_CONFIG, get_type_adapter
from .authenticate import Authenticate
from .token_authentication import TokenAuthentication


@final
class _OpenIdConfiguration(TypedDict):
    token_endpoint: str


@cache
def _fetch_token_endpoint_url(*, issuer_url: str) -> str:
    configuration_url = urljoin(f"{issuer_url}/", ".well-known/openid-configuration")
    response = httpx.get(configuration_url).raise_for_status()
    body = get_type_adapter(_OpenIdConfiguration).validate_json(response.content)
    return body["token_endpoint"]


@final
class _ResponseBody(TypedDict):
    access_token: str
    token_type: str


@final
@dataclass(config=_PYDANTIC_CONFIG, frozen=True, kw_only=True)
class OAuth2ResourceOwnerPasswordAuthentication(Authenticate):
    """Authenticate requests with OAuth 2's `Resource Owner Password Credentials Grant <https://datatracker.ietf.org/doc/html/rfc6749#section-4.3>`__.

    See Also:
        :attr:`atoti.OidcConfig.access_token_format`.
    """

    client_id: str
    client_secret: str
    issuer_url: str
    password: str
    scopes: AbstractSet[str] = frozenset()
    username: str

    @override
    def __call__(self, url: str) -> Mapping[str, str]:
        return self._token_authentication(url)

    @cached_property
    def _token_authentication(self) -> TokenAuthentication:
        url = _fetch_token_endpoint_url(issuer_url=self.issuer_url)
        response = httpx.post(
            url,
            data={
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "grant_type": "password",
                "password": self.password,
                "scope": " ".join(self.scopes),
                "username": self.username,
            },
        ).raise_for_status()
        body = get_type_adapter(_ResponseBody).validate_json(response.content)
        return TokenAuthentication(body["access_token"], token_type=body["token_type"])
