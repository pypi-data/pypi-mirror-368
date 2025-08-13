from typing import TypeAlias

from typing_extensions import TypeIs

from ._constant import Constant
from ._identification import ColumnIdentifier, HasIdentifier
from ._operation import (
    Condition,
    ConditionBound,
    Operation,
    OperationBound,
    RelationalCondition,
    RelationalOperator,
)

ColumnOperation: TypeAlias = Operation[ColumnIdentifier]

# Logical and membership conditions are not supported in UDAFs for now.
ColumnCondition: TypeAlias = RelationalCondition[
    ColumnIdentifier,
    RelationalOperator,
    ColumnIdentifier | ColumnOperation | Constant | None,
]


VariableColumnConvertible: TypeAlias = (
    ColumnCondition | ColumnOperation | HasIdentifier[ColumnIdentifier]
)
ColumnConvertible: TypeAlias = Constant | VariableColumnConvertible


def _is_column_base_operation(value: ConditionBound | OperationBound, /) -> bool:
    return value._identifier_types == frozenset([ColumnIdentifier])


def is_column_condition(value: object, /) -> TypeIs[ColumnCondition]:
    return isinstance(value, RelationalCondition) and _is_column_base_operation(value)


def is_column_operation(value: object, /) -> TypeIs[ColumnOperation]:
    return isinstance(value, Operation) and _is_column_base_operation(value)


def is_column_condition_or_operation(
    value: object,
    /,
) -> TypeIs[ColumnCondition | ColumnOperation]:
    return (
        is_column_condition(value)
        if isinstance(value, Condition)
        else is_column_operation(value)
    )


def is_variable_column_convertible(
    value: object,
    /,
) -> TypeIs[VariableColumnConvertible]:
    return (
        isinstance(value._identifier, ColumnIdentifier)
        if isinstance(value, HasIdentifier)
        else is_column_condition_or_operation(value)
    )
