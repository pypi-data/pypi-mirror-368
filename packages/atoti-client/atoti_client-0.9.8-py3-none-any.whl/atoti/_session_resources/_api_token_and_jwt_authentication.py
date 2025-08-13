from __future__ import annotations

from collections.abc import Mapping
from typing import final

from typing_extensions import override

from .._is_jwt_expired import is_jwt_expired
from .._py4j_client import Py4jClient
from ..authentication import Authenticate


@final
class ApiTokenAndJwtAuthentication(Authenticate):
    def __init__(self, token: str) -> None:
        self._jwt: str | None = None
        self._py4j_client: Py4jClient | None = None
        self._token: str | None = token

    def set_py4j_client(self, py4j_client: Py4jClient, /) -> None:
        assert self._py4j_client is None
        self._py4j_client = py4j_client
        # Not needed anymore, we will only use JWT from this point on
        self._token = None

    @override
    def __call__(self, _url: str, /) -> Mapping[str, str]:
        return {"Authorization": self._get_authorization_header()}

    def _get_authorization_header(self) -> str:
        if self._py4j_client is not None:
            if not self._jwt or is_jwt_expired(self._jwt):
                self._jwt = self._py4j_client.generate_jwt()
            return f"Jwt {self._jwt}"

        return f"API-TOKEN {self._token}"
