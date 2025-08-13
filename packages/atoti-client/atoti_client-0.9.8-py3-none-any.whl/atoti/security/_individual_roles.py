from __future__ import annotations

from collections.abc import Mapping, Set as AbstractSet
from pathlib import Path
from typing import Final, TypeAlias, final

from typing_extensions import override

from .._client import Client
from .._collections import DelegatingMutableMapping
from .._content_client import (
    SECURITY_ROOT_DIRECTORY as _SECURITY_ROOT_DIRECTORY,
    ContentTree,
    DirectoryContentTree,
    FileContentTree,
)
from .._identification import Role, UserName
from .._pydantic import get_type_adapter
from .._reserved_roles import ROLE_ADMIN as _ROLE_ADMIN

_DIRECTORY = f"{_SECURITY_ROOT_DIRECTORY}/individual_roles"
_PATH_TEMPLATE = f"{_DIRECTORY}/{{username}}.json"


_SerializedUserRoles: TypeAlias = AbstractSet[Role]


def _user_roles_from_content_tree(tree: ContentTree, /) -> _SerializedUserRoles:
    assert isinstance(tree, FileContentTree)
    return get_type_adapter(_SerializedUserRoles).validate_json(tree.entry.content)  # type: ignore[type-abstract]


@final
class IndividualRoles(DelegatingMutableMapping[UserName, AbstractSet[Role]]):
    def __init__(self, *, client: Client) -> None:
        self._client: Final = client

    @override
    def _get_delegate(
        self, *, key: UserName | None
    ) -> Mapping[UserName, AbstractSet[Role]]:
        path = _PATH_TEMPLATE.format(username=key) if key is not None else _DIRECTORY
        tree = self._client._require_content_client().get(path)

        if not tree:
            return {}

        if key is None:
            assert isinstance(tree, DirectoryContentTree)
            return {
                Path(filename).stem: _user_roles_from_content_tree(child_tree)
                for filename, child_tree in tree.children.items()
            }

        return {key: _user_roles_from_content_tree(tree)}

    @override
    def _update_delegate(self, other: Mapping[UserName, AbstractSet[Role]], /) -> None:
        content_client = self._client._require_content_client()

        for username, roles in other.items():
            path = _PATH_TEMPLATE.format(username=username)
            content_client.create(
                path,
                content=list(roles),
                owners={_ROLE_ADMIN},
                readers={_ROLE_ADMIN},
            )

    @override
    def _delete_delegate_keys(self, keys: AbstractSet[UserName], /) -> None:
        content_client = self._client._require_content_client()

        for username in keys:
            path = _PATH_TEMPLATE.format(username=username)
            content_client.delete(path)
