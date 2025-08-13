from collections.abc import Set as AbstractSet
from typing import Final, TypeAlias, final

from typing_extensions import override

from .._client import Client
from .._collections import DelegatingMutableSet
from .._content_client import (
    SECURITY_ROOT_DIRECTORY as _SECURITY_ROOT_DIRECTORY,
    FileContentTree,
)
from .._identification import Role
from .._pydantic import get_type_adapter
from .._reserved_roles import ROLE_ADMIN as _ROLE_ADMIN
from ._authentication_type import AuthenticationType

_PATH_TEMPLATE = (
    f"{_SECURITY_ROOT_DIRECTORY}/default_roles/{{authentication_type}}.json"
)


_SerializedDefaultRoles: TypeAlias = AbstractSet[Role]


@final
class DefaultRoles(DelegatingMutableSet[Role]):
    """Roles granted to users who have been granted no :attr:`individual <atoti.security.Security.individual_roles>` and :class:`mapped <atoti.security.role_mapping.RoleMapping>` roles."""

    def __init__(
        self, *, authentication_type: AuthenticationType, client: Client
    ) -> None:
        self._authentication_type: Final = authentication_type
        self._client: Final = client

    @property
    def _path(self) -> str:
        return _PATH_TEMPLATE.format(
            authentication_type=self._authentication_type,
        )

    @override
    def _get_delegate(self) -> AbstractSet[Role]:
        tree = self._client._require_content_client().get(self._path)

        if not tree:
            return set()

        assert isinstance(tree, FileContentTree)
        return get_type_adapter(_SerializedDefaultRoles).validate_json(  # type: ignore[type-abstract]
            tree.entry.content,
        )

    @override
    def _set_delegate(self, new_set: AbstractSet[Role], /) -> None:
        self._client._require_content_client().create(
            self._path,
            content=list(new_set),
            owners={_ROLE_ADMIN},
            readers={_ROLE_ADMIN},
        )
