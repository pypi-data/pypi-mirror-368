from __future__ import annotations

from collections.abc import Mapping, Set as AbstractSet
from typing import Final, final

from typing_extensions import override

from ._client import Client
from ._collections import DelegatingMutableMapping
from ._constant import Scalar
from ._cube_mask_condition import CubeMaskCondition, _CubeMaskLeafCondition
from ._identification import CubeName, Role
from ._operation import dnf_from_condition
from ._operation.operation import (
    HierarchyMembershipCondition,
    MembershipCondition,
    RelationalCondition,
)


@final
class Masks(DelegatingMutableMapping[Role, CubeMaskCondition]):
    def __init__(self, /, *, client: Client, cube_name: CubeName) -> None:
        self._client: Final = client
        self._cube_name: Final = cube_name

    @override
    def _get_delegate(self, *, key: Role | None) -> Mapping[Role, CubeMaskCondition]:
        return self._client._require_py4j_client().get_cube_mask(
            key, cube_name=self._cube_name
        )

    @override
    def _update_delegate(self, other: Mapping[Role, CubeMaskCondition], /) -> None:  # noqa: C901
        py4j_client = self._client._require_py4j_client()

        for role, condition in other.items():
            dnf: tuple[tuple[_CubeMaskLeafCondition, ...]] = dnf_from_condition(
                condition
            )
            (conjunct_conditions,) = dnf

            included_members: dict[str, AbstractSet[Scalar]] = {}
            included_member_paths: dict[str, AbstractSet[tuple[Scalar, ...]]] = {}
            excluded_members: dict[str, AbstractSet[Scalar]] = {}
            excluded_member_paths: dict[str, AbstractSet[tuple[Scalar, ...]]] = {}

            for leaf_condition in conjunct_conditions:
                hierarchy_java_description = leaf_condition.subject._java_description

                match leaf_condition:
                    case HierarchyMembershipCondition(
                        operator=operator, member_paths=member_paths
                    ):
                        match operator:
                            case "in":
                                included_member_paths[hierarchy_java_description] = (
                                    member_paths
                                )
                            case "not in":
                                excluded_member_paths[hierarchy_java_description] = (
                                    member_paths
                                )
                    case MembershipCondition(operator=operator, elements=elements):
                        match operator:
                            case "in":
                                included_members[hierarchy_java_description] = elements
                            case "not in":
                                excluded_members[hierarchy_java_description] = elements
                    case RelationalCondition(operator=operator, target=target):
                        match operator:
                            case "==":
                                included_members[hierarchy_java_description] = {target}
                            case "!=":
                                excluded_members[hierarchy_java_description] = {target}

            py4j_client.set_cube_mask(
                role,
                cube_name=self._cube_name,
                included_members=included_members,
                included_member_paths=included_member_paths,
                excluded_members=excluded_members,
                excluded_member_paths=excluded_member_paths,
            )

    @override
    def _delete_delegate_keys(self, keys: AbstractSet[Role], /) -> None:
        raise NotImplementedError("Cannot delete masking value.")
