from __future__ import annotations

from collections.abc import Mapping, Sequence, Set as AbstractSet
from typing import Final, TypeAlias, final

from typing_extensions import override

from ._client import Client
from ._collections import DelegatingMutableMapping
from ._constant import is_array
from ._graphql_client import (
    CreateDatabaseRestrictionInput,
    DatabaseRestrictionFragmentConditionDatabaseRestrictionMembershipCondition,
    DatabaseRestrictionFragmentConditionDatabaseRestrictionRelationalCondition,
    DatabaseRestrictionLeafConditionInput,
    DatabaseRestrictionMembershipConditionInput,
    DatabaseRestrictionMembershipConditionOperator,
    DatabaseRestrictionRelationalConditionInput,
    DatabaseRestrictionRelationalConditionOperator,
    DeleteDatabaseRestrictionInput,
)
from ._identification import (
    ColumnIdentifier,
    Role,
)
from ._operation import (
    MembershipCondition,
    RelationalCondition,
    condition_from_dnf,
    dnf_from_condition,
)
from ._reserved_roles import check_no_reserved_roles
from ._tables_restriction_condition import (
    TablesRestrictionCondition,
    _TablesRestrictionLeafCondition,
    _TablesRestrictionMembershipConditionOperator,
    _TablesRestrictionRelationalConditionOperator,
)

_GraphQLDatabaseLeafCondition: TypeAlias = (
    DatabaseRestrictionFragmentConditionDatabaseRestrictionMembershipCondition
    | DatabaseRestrictionFragmentConditionDatabaseRestrictionRelationalCondition
)


def _leaf_condition_from_graphql(
    condition: _GraphQLDatabaseLeafCondition, /
) -> _TablesRestrictionLeafCondition:
    match condition:
        case DatabaseRestrictionFragmentConditionDatabaseRestrictionMembershipCondition(
            subject=subject,
            membership_operator=operator,
            elements=_elements,
        ):
            elements = {element for element in _elements if not is_array(element)}
            assert len(elements) == len(_elements)
            del _elements

            match operator.value:
                case "IN":
                    membership_operator: _TablesRestrictionMembershipConditionOperator = "in"

            return MembershipCondition.of(
                subject=ColumnIdentifier._from_graphql(subject),
                operator=membership_operator,
                elements=elements,
            )
        case DatabaseRestrictionFragmentConditionDatabaseRestrictionRelationalCondition(
            subject=subject,
            relational_operator=operator,
            target=target,
        ):
            assert not is_array(target)

            match operator.value:
                case "EQ":
                    relational_operator: _TablesRestrictionRelationalConditionOperator = "=="

            return RelationalCondition(
                subject=ColumnIdentifier._from_graphql(subject),
                operator=relational_operator,
                target=target,
            )


def _condition_from_graphql(
    dnf: Sequence[Sequence[_GraphQLDatabaseLeafCondition]], /
) -> TablesRestrictionCondition:
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
    condition: _TablesRestrictionLeafCondition, /
) -> DatabaseRestrictionLeafConditionInput:
    match condition:
        case MembershipCondition(subject=subject, operator=operator, elements=elements):
            match operator:
                case "in":
                    membership_operator: DatabaseRestrictionMembershipConditionOperator = DatabaseRestrictionMembershipConditionOperator.IN

            return DatabaseRestrictionLeafConditionInput(
                membership=DatabaseRestrictionMembershipConditionInput(
                    subject=subject._graphql_input,
                    operator=membership_operator,
                    elements=list(elements),
                )
            )
        case RelationalCondition(subject=subject, operator=operator, target=target):
            match operator:
                case "==":
                    relational_operator: DatabaseRestrictionRelationalConditionOperator = DatabaseRestrictionRelationalConditionOperator.EQ

            return DatabaseRestrictionLeafConditionInput(
                relational=DatabaseRestrictionRelationalConditionInput(
                    subject=subject._graphql_input,
                    operator=relational_operator,
                    target=target,
                )
            )


def _condition_to_graphql(
    condition: TablesRestrictionCondition, /
) -> list[list[DatabaseRestrictionLeafConditionInput]]:
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
class Restrictions(DelegatingMutableMapping[Role, TablesRestrictionCondition]):
    def __init__(self, *, client: Client) -> None:
        self._client: Final = client

    @override
    def _get_delegate(
        self, *, key: Role | None
    ) -> Mapping[Role, TablesRestrictionCondition]:
        if key is None:
            restrictions = (
                self._client._require_graphql_client().get_database_restrictions()
            )
            return {
                restriction.role: _condition_from_graphql(restriction.condition)
                for restriction in restrictions.data_model.database.restrictions
            }

        restriction = self._client._require_graphql_client().get_database_restriction(
            role=key,
        )
        return (
            {}
            if restriction.data_model.database.restriction is None
            else {
                key: _condition_from_graphql(
                    restriction.data_model.database.restriction.condition
                )
            }
        )

    @override
    def _update_delegate(
        self, other: Mapping[Role, TablesRestrictionCondition], /
    ) -> None:
        check_no_reserved_roles(other)

        graphql_client = self._client._require_graphql_client()
        with graphql_client.mutation_batcher.batch():
            for role, condition in other.items():
                graphql_input = CreateDatabaseRestrictionInput(
                    condition=_condition_to_graphql(condition),
                    role=role,
                )
                graphql_client.create_database_restriction(input=graphql_input)

    @override
    def _delete_delegate_keys(self, keys: AbstractSet[Role], /) -> None:
        if keys:
            graphql_client = self._client._require_graphql_client()

            with graphql_client.mutation_batcher.batch():
                for role in keys:
                    graphql_input = DeleteDatabaseRestrictionInput(
                        role=role,
                    )
                    graphql_client.delete_database_restriction(input=graphql_input)
