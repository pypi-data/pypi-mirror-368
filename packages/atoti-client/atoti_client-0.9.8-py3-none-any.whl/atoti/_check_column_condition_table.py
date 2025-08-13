from itertools import chain
from typing import Literal, TypeAlias

from ._identification import ColumnIdentifier, TableIdentifier
from ._operation import (
    LogicalCondition,
    LogicalOperator,
    MembershipCondition,
    MembershipConditionElementBound,
    MembershipOperator,
    RelationalCondition,
    RelationalConditionTargetBound,
    RelationalOperator,
    dnf_from_condition,
)

_ColumnLeafCondition: TypeAlias = (
    MembershipCondition[
        ColumnIdentifier, MembershipOperator, MembershipConditionElementBound
    ]
    | RelationalCondition[
        ColumnIdentifier,
        RelationalOperator,
        RelationalConditionTargetBound,
    ]
)
_ColumnCondition: TypeAlias = (
    _ColumnLeafCondition | LogicalCondition[_ColumnLeafCondition, LogicalOperator]
)


def check_column_condition_table(
    condition: _ColumnCondition,
    /,
    *,
    attribute_name: Literal["subject", "target"],
    expected_table_identifier: TableIdentifier,
) -> None:
    error_message_template = f"Expected the {{attribute_name}} of the condition to belong to the table `{expected_table_identifier.table_name}` but got `{{table_name}}`."

    dnf = dnf_from_condition(condition)

    for leaf_condition in chain.from_iterable(dnf):
        match attribute_name:
            case "subject":
                if leaf_condition.subject.table_identifier != expected_table_identifier:  # type: ignore[union-attr]
                    raise ValueError(
                        error_message_template.format(
                            attribute_name=attribute_name,
                            table_name=leaf_condition.subject.table_identifier.table_name,  # type: ignore[union-attr]
                        ),
                    )
            case "target":
                assert isinstance(leaf_condition, RelationalCondition)
                assert isinstance(leaf_condition.target, ColumnIdentifier)
                if leaf_condition.target.table_identifier != expected_table_identifier:
                    raise ValueError(
                        error_message_template.format(
                            attribute_name=attribute_name,
                            table_name=leaf_condition.target.table_identifier.table_name,
                        ),
                    )
