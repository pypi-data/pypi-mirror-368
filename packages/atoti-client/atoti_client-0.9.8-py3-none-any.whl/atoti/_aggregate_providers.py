from collections.abc import Mapping, Sequence, Set as AbstractSet
from typing import Final, TypeAlias, final

from typing_extensions import override

from ._client import Client
from ._collections import DelegatingMutableMapping
from ._constant import is_array
from ._graphql_client import (
    AggregateProviderFilterFragmentFilterAggregateProviderFilterMembershipCondition,
    AggregateProviderFilterFragmentFilterAggregateProviderFilterRelationalCondition,
    AggregateProviderFilterLeafConditionInput,
    AggregateProviderFilterMembershipConditionInput,
    AggregateProviderFilterMembershipConditionOperator,
    AggregateProviderFilterRelationalConditionInput,
    AggregateProviderFilterRelationalConditionOperator,
    AggregateProviderFragment,
    AggregateProviderPluginKey,
    CreateAggregateProviderInput,
    DeleteAggregateProviderInput,
    create_delete_status_validator,
)
from ._identification import (
    CubeIdentifier,
    LevelIdentifier,
    MeasureIdentifier,
    identify,
)
from ._operation import condition_from_dnf, dnf_from_condition
from ._operation.operation import MembershipCondition, RelationalCondition
from .aggregate_provider import (
    AggregateProvider,
    _AggregateProviderFilterCondition,
    _AggregateProviderFilterLeafCondition,
    _AggregateProviderFilterMembershipConditionOperator,
    _AggregateProviderFilterRelationalConditionOperator,
    _AggregateProviderPluginKey,
)

_GraphQlFindAggregateProviderLeafFilter: TypeAlias = (
    AggregateProviderFilterFragmentFilterAggregateProviderFilterMembershipCondition
    | AggregateProviderFilterFragmentFilterAggregateProviderFilterRelationalCondition
)


def _filter_leaf_condition_from_graphql(
    condition: _GraphQlFindAggregateProviderLeafFilter, /
) -> _AggregateProviderFilterLeafCondition:
    match condition:
        case AggregateProviderFilterFragmentFilterAggregateProviderFilterMembershipCondition(
            subject=subject,
            membership_operator=operator,
            elements=_elements,
        ):
            elements = {element for element in _elements if not is_array(element)}
            assert len(elements) == len(_elements)
            del _elements

            match operator.value:
                case "IN":
                    membership_operator: _AggregateProviderFilterMembershipConditionOperator = "in"

            return MembershipCondition.of(
                subject=LevelIdentifier._from_graphql(subject),
                operator=membership_operator,
                elements=elements,
            )
        case AggregateProviderFilterFragmentFilterAggregateProviderFilterRelationalCondition(
            subject=subject,
            relational_operator=operator,
            target=target,
        ):
            assert not is_array(target)

            match operator.value:
                case "EQ":
                    relational_operator: _AggregateProviderFilterRelationalConditionOperator = "=="

            return RelationalCondition(
                subject=LevelIdentifier._from_graphql(subject),
                operator=relational_operator,
                target=target,
            )


def _filter_from_graphql(
    dnf: Sequence[Sequence[_GraphQlFindAggregateProviderLeafFilter]] | None, /
) -> _AggregateProviderFilterCondition | None:
    match dnf:
        case None:
            return None
        case [graphql_conjunct_conditions]:
            conjunct_conditions = [
                _filter_leaf_condition_from_graphql(leaf_condition)
                for leaf_condition in graphql_conjunct_conditions
            ]
            return condition_from_dnf((conjunct_conditions,))
        case _:
            raise AssertionError(f"Unexpected disjunctive normal form: {dnf}.")


def _plugin_key_from_graphql(  # type: ignore[return]
    plugin_key: AggregateProviderPluginKey, /
) -> _AggregateProviderPluginKey:
    match plugin_key.value:
        case "BITMAP":
            return "bitmap"
        case "LEAF":
            return "leaf"


def _from_graphql(
    aggregate_provider: AggregateProviderFragment, /
) -> AggregateProvider:
    return AggregateProvider(
        filter=None
        if aggregate_provider.filter is None
        else _filter_from_graphql(aggregate_provider.filter),
        levels=None
        if aggregate_provider.levels is None
        else {
            LevelIdentifier._from_graphql(level) for level in aggregate_provider.levels
        },
        measures=None
        if aggregate_provider.measures is None
        else {
            MeasureIdentifier._from_graphql(measure)
            for measure in aggregate_provider.measures
        },
        key=_plugin_key_from_graphql(aggregate_provider.plugin_key),
        partitioning=aggregate_provider.partitioning,
    )


def _filter_leaf_condition_to_graphql(
    condition: _AggregateProviderFilterLeafCondition, /
) -> AggregateProviderFilterLeafConditionInput:
    match condition:
        case MembershipCondition(subject=subject, operator=operator, elements=elements):
            match operator:
                case "in":
                    membership_operator: AggregateProviderFilterMembershipConditionOperator = AggregateProviderFilterMembershipConditionOperator.IN

            return AggregateProviderFilterLeafConditionInput(
                membership=AggregateProviderFilterMembershipConditionInput(
                    subject=subject._graphql_input,
                    operator=membership_operator,
                    elements=list(elements),
                )
            )

        case RelationalCondition(subject=subject, operator=operator, target=target):
            match operator:
                case "==":
                    relational_operator: AggregateProviderFilterRelationalConditionOperator = AggregateProviderFilterRelationalConditionOperator.EQ

            return AggregateProviderFilterLeafConditionInput(
                relational=AggregateProviderFilterRelationalConditionInput(
                    subject=subject._graphql_input,
                    operator=relational_operator,
                    target=target,
                )
            )


def _filter_to_graphql(
    _filter: _AggregateProviderFilterCondition | None, /
) -> list[list[AggregateProviderFilterLeafConditionInput]] | None:
    match _filter:
        case None:
            return None
        case _:
            dnf = dnf_from_condition(_filter)
            return [
                [
                    _filter_leaf_condition_to_graphql(leaf_condition)  # type: ignore[arg-type]
                    for leaf_condition in conjunct_conditions
                ]
                for conjunct_conditions in dnf
            ]


def _plugin_key_to_graphql(
    plugin_key: _AggregateProviderPluginKey, /
) -> AggregateProviderPluginKey:
    match plugin_key:
        case "bitmap":
            return AggregateProviderPluginKey.BITMAP
        case "leaf":
            return AggregateProviderPluginKey.LEAF


def _get_create_aggregate_provider_input(
    aggregate_provider: AggregateProvider,
    /,
    *,
    cube_identifier: CubeIdentifier,
    name: str,
) -> CreateAggregateProviderInput:
    graphql_input = CreateAggregateProviderInput(
        cube_name=cube_identifier.cube_name,
        name=name,
        plugin_key=_plugin_key_to_graphql(aggregate_provider.key),
    )

    _filter = _filter_to_graphql(aggregate_provider.filter)
    if _filter is not None:
        graphql_input.filter = _filter

    if aggregate_provider.levels is not None:
        graphql_input.level_identifiers = [
            identify(level)._graphql_input for level in aggregate_provider.levels
        ]

    if aggregate_provider.measures is not None:
        graphql_input.measure_names = [
            identify(measure).measure_name for measure in aggregate_provider.measures
        ]

    if aggregate_provider.partitioning is not None:
        graphql_input.partitioning = aggregate_provider.partitioning

    return graphql_input


@final
class AggregateProviders(DelegatingMutableMapping[str, AggregateProvider]):
    def __init__(self, cube_identifier: CubeIdentifier, /, *, client: Client):
        self._client: Final = client
        self._cube_identifier: Final = cube_identifier

    @override
    def _get_delegate(
        self,
        *,
        key: str | None,
    ) -> Mapping[str, AggregateProvider]:
        if key is None:
            output = self._client._require_graphql_client().get_aggregate_providers(
                cube_name=self._cube_identifier.cube_name,
            )
            return {
                provider.name: _from_graphql(provider)
                for provider in output.data_model.cube.aggregate_providers
            }

        output = self._client._require_graphql_client().find_aggregate_provider(  # type: ignore[assignment] # See https://github.com/python/mypy/issues/12968.
            cube_name=self._cube_identifier.cube_name,
            name=key,
        )
        cube = output.data_model.cube

        return (
            {}
            if cube.aggregate_provider is None  # type: ignore[attr-defined]
            else {key: _from_graphql(cube.aggregate_provider)}  # type: ignore[attr-defined]
        )

    @override
    def _update_delegate(self, other: Mapping[str, AggregateProvider], /) -> None:
        graphql_client = self._client._require_graphql_client()

        with graphql_client.mutation_batcher.batch():
            for name, aggregate_provider in other.items():
                graphql_input = _get_create_aggregate_provider_input(
                    aggregate_provider, cube_identifier=self._cube_identifier, name=name
                )
                graphql_client.create_aggregate_provider(input=graphql_input)

    @override
    def _delete_delegate_keys(self, keys: AbstractSet[str], /) -> None:
        graphql_client = self._client._require_graphql_client()

        with graphql_client.mutation_batcher.batch():
            for key in keys:
                graphql_input = DeleteAggregateProviderInput(
                    cube_name=self._cube_identifier.cube_name,
                    name=key,
                )
                graphql_client.delete_aggregate_provider(
                    input=graphql_input
                ).set_output_validator(
                    create_delete_status_validator(
                        key, lambda output: output.delete_aggregate_provider.status
                    )
                )
