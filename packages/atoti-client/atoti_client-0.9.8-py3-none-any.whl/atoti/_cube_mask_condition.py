from typing import Literal, TypeAlias

from ._constant import Scalar
from ._identification import HierarchyIdentifier
from ._operation import (
    EqualityOperator,
    HierarchyMembershipConditionBound,
    LogicalCondition,
    MembershipCondition,
    MembershipOperator,
    RelationalCondition,
)

_CubeMaskLeafCondition: TypeAlias = (
    HierarchyMembershipConditionBound
    | MembershipCondition[HierarchyIdentifier, MembershipOperator, Scalar]
    | RelationalCondition[HierarchyIdentifier, EqualityOperator, Scalar]
)

CubeMaskCondition: TypeAlias = (
    _CubeMaskLeafCondition | LogicalCondition[_CubeMaskLeafCondition, Literal["&"]]
)
