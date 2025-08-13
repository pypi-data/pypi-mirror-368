from __future__ import annotations

from collections.abc import Mapping, Sequence, Set as AbstractSet
from typing import Final, TypeAlias, final

from typing_extensions import override

from ._client import Client
from ._collections import DelegatingMutableMapping
from ._constant import is_array
from ._cube_restriction_condition import (
    CubeRestrictionCondition,
    _CubeRestrictionLeafCondition,
    _CubeRestrictionMembershipConditionOperator,
    _CubeRestrictionRelationalConditionOperator,
)
from ._graphql_client import (
    CreateCubeRestrictionInput,
    CubeRestrictionFragmentConditionCubeRestrictionMembershipCondition,
    CubeRestrictionFragmentConditionCubeRestrictionRelationalCondition,
    CubeRestrictionLeafConditionInput,
    CubeRestrictionMembershipConditionInput,
    CubeRestrictionMembershipConditionOperator,
    CubeRestrictionRelationalConditionInput,
    CubeRestrictionRelationalConditionOperator,
    DeleteCubeRestrictionInput,
    create_delete_status_validator,
)
from ._identification import CubeIdentifier, LevelIdentifier, Role
from ._operation import (
    MembershipCondition,
    RelationalCondition,
    condition_from_dnf,
    dnf_from_condition,
)
from ._reserved_roles import check_no_reserved_roles

_GraphQlCubeLeafCondition: TypeAlias = (
    CubeRestrictionFragmentConditionCubeRestrictionMembershipCondition
    | CubeRestrictionFragmentConditionCubeRestrictionRelationalCondition
)


def _leaf_condition_from_graphql(
    condition: _GraphQlCubeLeafCondition, /
) -> _CubeRestrictionLeafCondition:
    match condition:
        case CubeRestrictionFragmentConditionCubeRestrictionMembershipCondition(
            subject=subject, membership_operator=operator, elements=_elements
        ):
            elements = {element for element in _elements if not is_array(element)}
            assert len(elements) == len(_elements)
            del _elements

            match operator.value:
                case "IN":
                    membership_operator: _CubeRestrictionMembershipConditionOperator = (
                        "in"
                    )

            return MembershipCondition.of(
                subject=LevelIdentifier._from_graphql(subject),
                operator=membership_operator,
                elements=elements,
            )
        case CubeRestrictionFragmentConditionCubeRestrictionRelationalCondition(
            subject=subject,
            relational_operator=operator,
            target=target,
        ):
            assert not is_array(target)

            match operator.value:
                case "EQ":
                    relational_operator: _CubeRestrictionRelationalConditionOperator = (
                        "=="
                    )

            return RelationalCondition(
                subject=LevelIdentifier._from_graphql(subject),
                operator=relational_operator,
                target=target,
            )


def _condition_from_graphql(
    dnf: Sequence[Sequence[_GraphQlCubeLeafCondition]], /
) -> CubeRestrictionCondition:
    match dnf:
        case [graphql_conjunct_conditions]:
            conjunct_conditions = [
                _leaf_condition_from_graphql(condition)
                for condition in graphql_conjunct_conditions
            ]
            return condition_from_dnf((conjunct_conditions,))
        case _:
            raise AssertionError(f"Unexpected disjunctive normal form: {dnf}.")


def _leaf_condition_to_graphql(
    condition: _CubeRestrictionLeafCondition, /
) -> CubeRestrictionLeafConditionInput:
    match condition:
        case MembershipCondition(subject=subject, operator=operator, elements=elements):
            match operator:
                case "in":
                    membership_operator: CubeRestrictionMembershipConditionOperator = (
                        CubeRestrictionMembershipConditionOperator.IN
                    )

            return CubeRestrictionLeafConditionInput(
                membership=CubeRestrictionMembershipConditionInput(
                    subject=subject._graphql_input,
                    operator=membership_operator,
                    elements=list(elements),
                )
            )
        case RelationalCondition(subject=subject, operator=operator, target=target):
            match operator:
                case "==":
                    relational_operator: CubeRestrictionRelationalConditionOperator = (
                        CubeRestrictionRelationalConditionOperator.EQ
                    )

            return CubeRestrictionLeafConditionInput(
                relational=CubeRestrictionRelationalConditionInput(
                    subject=subject._graphql_input,
                    operator=relational_operator,
                    target=target,
                )
            )


def _condition_to_graphql(
    condition: CubeRestrictionCondition, /
) -> list[list[CubeRestrictionLeafConditionInput]]:
    dnf = dnf_from_condition(condition)
    return [
        [
            _leaf_condition_to_graphql(
                leaf_condition  # type: ignore[arg-type]
            )
            for leaf_condition in conjunct_conditions
        ]
        for conjunct_conditions in dnf
    ]


@final
class CubeRestrictions(DelegatingMutableMapping[Role, CubeRestrictionCondition]):
    def __init__(self, cube_identifier: CubeIdentifier, /, *, client: Client) -> None:
        self._client: Final = client
        self._cube_identifier: Final = cube_identifier

    @override
    def _get_delegate(
        self, *, key: Role | None
    ) -> Mapping[str, CubeRestrictionCondition]:
        if key is None:
            output = self._client._require_graphql_client().get_cube_restrictions(
                cube_name=self._cube_identifier.cube_name
            )
            return {
                restriction.role: _condition_from_graphql(restriction.condition)
                for restriction in output.data_model.cube.restrictions
            }

        output = self._client._require_graphql_client().find_cube_restriction(  # type: ignore[assignment] # See https://github.com/python/mypy/issues/12968.
            cube_name=self._cube_identifier.cube_name,
            role=key,
        )
        cube = output.data_model.cube
        return (
            {}
            if cube.restriction is None  # type: ignore[attr-defined]
            else {key: _condition_from_graphql(cube.restriction.condition)}  # type: ignore[attr-defined]
        )

    @override
    def _update_delegate(
        self, other: Mapping[Role, CubeRestrictionCondition], /
    ) -> None:
        check_no_reserved_roles(other)

        graphql_client = self._client._require_graphql_client()

        with graphql_client.mutation_batcher.batch():
            for role, condition in other.items():
                graphql_input = CreateCubeRestrictionInput(
                    condition=_condition_to_graphql(condition),
                    cube_name=self._cube_identifier.cube_name,
                    role=role,
                )
                graphql_client.create_cube_restriction(input=graphql_input)

    @override
    def _delete_delegate_keys(self, keys: AbstractSet[Role], /) -> None:
        graphql_client = self._client._require_graphql_client()

        with graphql_client.mutation_batcher.batch():
            for key in keys:
                graphql_input = DeleteCubeRestrictionInput(
                    cube_name=self._cube_identifier.cube_name,
                    role=key,
                )
                graphql_client.delete_cube_restriction(
                    input=graphql_input
                ).set_output_validator(
                    create_delete_status_validator(
                        key, lambda output: output.delete_cube_restriction.status
                    )
                )
