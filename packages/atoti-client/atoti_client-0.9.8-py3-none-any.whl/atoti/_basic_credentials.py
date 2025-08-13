from __future__ import annotations

from collections.abc import Mapping, Set as AbstractSet
from typing import Final, final

from typing_extensions import override

from ._client import Client
from ._collections import DelegatingMutableMapping
from ._identification import UserName
from .security._authentication_type import AuthenticationType

_BASIC_AUTHENTICATION_TYPE: AuthenticationType = "BASIC"
_REDACTED_PASSWORD = "**REDACTED**"  # noqa: S105


@final
class BasicCredentials(DelegatingMutableMapping[UserName, str]):
    def __init__(self, *, client: Client) -> None:
        self._client: Final = client

    @override
    def _get_delegate(self, *, key: UserName | None) -> Mapping[UserName, str]:
        return {
            username: _REDACTED_PASSWORD
            for username in self._client._require_py4j_client()
            ._enterprise_api()
            .getUsers(
                _BASIC_AUTHENTICATION_TYPE,
            )
            if key is None or username == key
        }

    @override
    def _update_delegate(self, other: Mapping[UserName, str], /) -> None:
        py4j_client = self._client._require_py4j_client()

        usernames = set(self)
        for username, password in other.items():
            if username in usernames:
                py4j_client._enterprise_api().updateUserPassword(
                    username,
                    password,
                    _BASIC_AUTHENTICATION_TYPE,
                )
            else:
                py4j_client._enterprise_api().createUser(
                    username,
                    password,
                    _BASIC_AUTHENTICATION_TYPE,
                )

    @override
    def _delete_delegate_keys(self, keys: AbstractSet[UserName], /) -> None:
        py4j_client = self._client._require_py4j_client()

        for username in keys:
            py4j_client._enterprise_api().deleteUser(
                username,
                _BASIC_AUTHENTICATION_TYPE,
            )
