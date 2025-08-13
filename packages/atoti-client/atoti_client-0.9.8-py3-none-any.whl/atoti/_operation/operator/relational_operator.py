from typing import Literal, TypeAlias

from typing_extensions import overload

EqualityOperator: TypeAlias = Literal["==", "!="]
InequalityOperator: TypeAlias = Literal[">=", ">", "<=", "<"]

RelationalOperator: TypeAlias = EqualityOperator | InequalityOperator
"""See https://en.wikipedia.org/wiki/Relational_operator."""


@overload
def invert_relational_operator(operator: Literal["=="], /) -> Literal["!="]: ...
@overload
def invert_relational_operator(operator: Literal["!="], /) -> Literal["=="]: ...
@overload
def invert_relational_operator(operator: EqualityOperator, /) -> EqualityOperator: ...
@overload
def invert_relational_operator(operator: Literal[">="], /) -> Literal["<"]: ...
@overload
def invert_relational_operator(operator: Literal[">"], /) -> Literal["<="]: ...
@overload
def invert_relational_operator(operator: Literal["<="], /) -> Literal[">"]: ...
@overload
def invert_relational_operator(operator: Literal["<"], /) -> Literal[">="]: ...
@overload
def invert_relational_operator(
    operator: InequalityOperator, /
) -> InequalityOperator: ...
@overload
def invert_relational_operator(
    operator: RelationalOperator, /
) -> RelationalOperator: ...
def invert_relational_operator(operator: RelationalOperator, /) -> RelationalOperator:
    match operator:
        case "==":
            return "!="
        case "!=":
            return "=="
        case ">=":
            return "<"
        case ">":
            return "<="
        case "<=":
            return ">"
        case "<":
            return ">="
