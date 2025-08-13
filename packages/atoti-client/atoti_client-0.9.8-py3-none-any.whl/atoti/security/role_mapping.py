from __future__ import annotations

from collections.abc import Mapping, Set as AbstractSet
from typing import Final, TypeAlias, final

from typing_extensions import override

from .._client import Client
from .._collections import DelegatingMutableMapping
from .._content_client import (
    SECURITY_ROOT_DIRECTORY as _SECURITY_ROOT_DIRECTORY,
    FileContentTree,
)
from .._identification import Role
from .._pydantic import get_type_adapter
from .._reserved_roles import ROLE_ADMIN as _ROLE_ADMIN
from ._authentication_type import AuthenticationType

_PATH_TEMPLATE = f"{_SECURITY_ROOT_DIRECTORY}/role_mapping/{{authentication_type}}.json"

_RoleMapping: TypeAlias = Mapping[str, AbstractSet[Role]]


@final
class RoleMapping(DelegatingMutableMapping[str, AbstractSet[Role]]):
    """Mapping from role or username coming from the authentication provider to roles to use in the session."""

    def __init__(
        self,
        *,
        authentication_type: AuthenticationType,
        client: Client,
    ) -> None:
        self._authentication_type: Final = authentication_type
        self._client: Final = client

    @property
    def _path(self) -> str:
        return _PATH_TEMPLATE.format(
            authentication_type=self._authentication_type,
        )

    @override
    def _get_delegate(self, *, key: str | None) -> _RoleMapping:
        tree = self._client._require_content_client().get(self._path)

        if not tree:
            return {}

        assert isinstance(tree, FileContentTree)
        role_mapping = get_type_adapter(_RoleMapping).validate_json(tree.entry.content)  # type: ignore[type-abstract]
        return role_mapping if key is None else {key: role_mapping[key]}

    @override
    def _update_delegate(self, other: Mapping[str, AbstractSet[Role]], /) -> None:
        role_mapping = {**self, **other}
        self._client._require_content_client().create(
            self._path,
            content={
                role: list(mapped_role_names)
                for role, mapped_role_names in role_mapping.items()
            },
            owners={_ROLE_ADMIN},
            readers={_ROLE_ADMIN},
        )

    @override
    def _delete_delegate_keys(self, keys: AbstractSet[str], /) -> None:
        role_mapping = dict(self)
        for key in keys:
            del role_mapping[key]
        self._client._require_content_client().create(
            self._path,
            content=role_mapping,
            owners={_ROLE_ADMIN},
            readers={_ROLE_ADMIN},
        )
