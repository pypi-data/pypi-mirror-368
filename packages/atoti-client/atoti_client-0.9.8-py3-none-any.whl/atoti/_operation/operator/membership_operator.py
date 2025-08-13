from typing import Literal

from typing_extensions import overload

MembershipOperator = Literal["in", "not in"]
"""See https://docs.python.org/3/reference/expressions.html#membership-test-operations."""


@overload
def invert_membership_operator(operator: Literal["in"], /) -> Literal["not in"]: ...
@overload
def invert_membership_operator(operator: Literal["not in"], /) -> Literal["in"]: ...
@overload
def invert_membership_operator(
    operator: MembershipOperator, /
) -> MembershipOperator: ...
def invert_membership_operator(operator: MembershipOperator, /) -> MembershipOperator:
    match operator:
        case "in":
            return "not in"
        case "not in":
            return "in"
