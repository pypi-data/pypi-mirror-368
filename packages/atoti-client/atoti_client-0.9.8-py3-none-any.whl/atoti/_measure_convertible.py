from __future__ import annotations

from typing import TypeAlias

from typing_extensions import TypeIs

from ._constant import Constant, Scalar
from ._identification import (
    HasIdentifier,
    HierarchyIdentifier,
    LevelIdentifier,
    MeasureIdentifier,
)
from ._operation import (
    Condition,
    ConditionBound,
    HierarchyMembershipCondition,
    LogicalCondition,
    LogicalOperator,
    MembershipCondition,
    MembershipConditionElementBound,
    MembershipOperator,
    Operation,
    OperationBound,
    RelationalCondition,
    RelationalOperator,
)

MeasureConvertibleIdentifier: TypeAlias = (
    HierarchyIdentifier | LevelIdentifier | MeasureIdentifier
)

MeasureOperation: TypeAlias = Operation[MeasureConvertibleIdentifier]

_MeasureLeafCondition: TypeAlias = (
    HierarchyMembershipCondition[MembershipOperator, Scalar]
    | MembershipCondition[
        LevelIdentifier | MeasureIdentifier,
        MembershipOperator,
        MembershipConditionElementBound,
    ]
    | RelationalCondition[
        LevelIdentifier | MeasureIdentifier | MeasureOperation,
        RelationalOperator,
        Constant | MeasureConvertibleIdentifier | MeasureOperation | None,
    ]
)
MeasureCondition: TypeAlias = (
    _MeasureLeafCondition | LogicalCondition[_MeasureLeafCondition, LogicalOperator]
)

VariableMeasureOperand: TypeAlias = (
    MeasureCondition | MeasureOperation | MeasureConvertibleIdentifier
)
MeasureOperand: TypeAlias = Constant | VariableMeasureOperand

VariableMeasureConvertible: TypeAlias = (
    HasIdentifier[MeasureConvertibleIdentifier] | MeasureCondition | MeasureOperation
)
MeasureConvertible: TypeAlias = Constant | VariableMeasureConvertible


def _is_measure_base_operation(value: ConditionBound | OperationBound, /) -> bool:
    # It is not a measure `BaseOperation` if there are some unexpected identifier types.
    return not (
        value._identifier_types
        - {HierarchyIdentifier, LevelIdentifier, MeasureIdentifier}
    )


def is_measure_condition(value: object, /) -> TypeIs[MeasureCondition]:
    return isinstance(value, Condition) and _is_measure_base_operation(value)


def is_measure_operation(value: object, /) -> TypeIs[MeasureOperation]:
    return isinstance(value, Operation) and _is_measure_base_operation(value)


def is_measure_condition_or_operation(
    value: object,
    /,
) -> TypeIs[MeasureCondition | MeasureOperation]:
    return (
        is_measure_condition(value)
        if isinstance(value, Condition)
        else is_measure_operation(value)
    )


def is_variable_measure_convertible(
    value: object,
    /,
) -> TypeIs[VariableMeasureConvertible]:
    return (
        isinstance(
            value._identifier,
            HierarchyIdentifier | LevelIdentifier | MeasureIdentifier,
        )
        if isinstance(value, HasIdentifier)
        else is_measure_condition_or_operation(value)
    )
