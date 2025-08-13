from __future__ import annotations

from typing import Literal, TypeAlias

from ._constant import Constant
from ._identification import ColumnIdentifier
from ._operation import (
    LogicalCondition,
    LogicalOperator,
    MembershipCondition,
    RelationalCondition,
    RelationalOperator,
)

_TableQueryFilterLeafCondition: TypeAlias = (
    MembershipCondition[ColumnIdentifier, Literal["in"], Constant]
    | RelationalCondition[
        ColumnIdentifier,
        RelationalOperator,
        Constant,
    ]
)
TableQueryFilterCondition: TypeAlias = (
    _TableQueryFilterLeafCondition
    | LogicalCondition[_TableQueryFilterLeafCondition, LogicalOperator]
)
