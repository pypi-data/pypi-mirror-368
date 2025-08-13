from __future__ import annotations

from typing import Literal, TypeAlias

from ._constant import Scalar
from ._identification import ColumnIdentifier
from ._operation import LogicalCondition, MembershipCondition, RelationalCondition

_TablesRestrictionMembershipConditionOperator: TypeAlias = Literal["in"]
_TablesRestrictionRelationalConditionOperator: TypeAlias = Literal["=="]
_TablesRestrictionLeafCondition: TypeAlias = (
    MembershipCondition[
        ColumnIdentifier, _TablesRestrictionMembershipConditionOperator, Scalar
    ]
    | RelationalCondition[
        ColumnIdentifier, _TablesRestrictionRelationalConditionOperator, Scalar
    ]
)
TablesRestrictionCondition: TypeAlias = (
    _TablesRestrictionLeafCondition
    | LogicalCondition[_TablesRestrictionLeafCondition, Literal["&"]]
)
