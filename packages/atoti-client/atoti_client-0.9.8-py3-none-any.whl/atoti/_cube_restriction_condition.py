from __future__ import annotations

from typing import Literal, TypeAlias

from ._constant import Scalar
from ._identification import LevelIdentifier
from ._operation.operation import (
    LogicalCondition,
    MembershipCondition,
    RelationalCondition,
)

_CubeRestrictionMembershipConditionOperator: TypeAlias = Literal["in"]
_CubeRestrictionRelationalConditionOperator: TypeAlias = Literal["=="]
_CubeRestrictionLeafCondition: TypeAlias = (
    MembershipCondition[
        LevelIdentifier, _CubeRestrictionMembershipConditionOperator, Scalar
    ]
    | RelationalCondition[
        LevelIdentifier, _CubeRestrictionRelationalConditionOperator, Scalar
    ]
)
CubeRestrictionCondition: TypeAlias = (
    _CubeRestrictionLeafCondition
    | LogicalCondition[_CubeRestrictionLeafCondition, Literal["&"]]
)
