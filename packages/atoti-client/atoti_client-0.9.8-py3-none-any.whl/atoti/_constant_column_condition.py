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

ConstantColumnLeafCondition: TypeAlias = (
    MembershipCondition[ColumnIdentifier, Literal["in"], Constant | None]
    | RelationalCondition[ColumnIdentifier, RelationalOperator, Constant | None]
)
ConstantColumnCondition: TypeAlias = (
    ConstantColumnLeafCondition
    | LogicalCondition[ConstantColumnLeafCondition, LogicalOperator]
)
