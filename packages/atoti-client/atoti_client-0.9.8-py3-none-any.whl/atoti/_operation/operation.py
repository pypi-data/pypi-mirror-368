from __future__ import annotations

import math
from abc import ABC, abstractmethod
from collections.abc import Sequence, Set as AbstractSet
from dataclasses import KW_ONLY, dataclass as _dataclass
from functools import cached_property
from itertools import chain
from typing import (
    Annotated,
    Generic,
    Literal,
    NoReturn,
    TypeAlias,
    TypeVar,
    Union,
    cast,
    final,
    overload,
)

from pydantic import AfterValidator, BaseModel, Field, SerializeAsAny, model_validator
from pydantic.dataclasses import dataclass
from typing_extensions import Self, assert_type, override

from .._collections import FrozenSequence
from .._constant import Constant, Scalar, ScalarT_co, is_scalar
from .._identification import (
    HasIdentifier,
    HierarchyIdentifier,
    Identifier,
    IdentifierT_co,
    LevelIdentifier,
    LevelName,
)
from .._pydantic import PYDANTIC_CONFIG as _PYDANTIC_CONFIG
from ._other_identifier import OtherIdentifierT_co
from .operator import (
    EqualityOperator,
    LogicalOperator,
    MembershipOperator,
    NAryArithmeticOperator,
    RelationalOperator,
    UnaryArithmeticOperator,
    invert_membership_operator,
    invert_relational_operator,
)

_ConstantT = TypeVar("_ConstantT", bound=Constant)


@overload
def convert_to_operand(value: None, /) -> None: ...


@overload
def convert_to_operand(value: _ConstantT, /) -> _ConstantT: ...


@overload
def convert_to_operand(value: HasIdentifier[IdentifierT_co], /) -> IdentifierT_co: ...


@overload
def convert_to_operand(
    value: OperandCondition[IdentifierT_co],
    /,
) -> OperandCondition[IdentifierT_co]: ...


@overload
def convert_to_operand(
    value: Operation[IdentifierT_co],
    /,
) -> Operation[IdentifierT_co]: ...


def convert_to_operand(
    value: OperandCondition[IdentifierT_co]
    | Constant
    | HasIdentifier[IdentifierT_co]
    | Operation[IdentifierT_co]
    | None,
    /,
) -> Operand[IdentifierT_co] | None:
    return value._identifier if isinstance(value, HasIdentifier) else value


class OperandConvertible(Generic[IdentifierT_co], ABC):
    @property
    @abstractmethod
    def _operation_operand(self) -> _UnconditionalVariableOperand[IdentifierT_co]: ...

    def isnull(
        self,
    ) -> RelationalCondition[
        _UnconditionalVariableOperand[IdentifierT_co], Literal["=="], None
    ]:
        """Return a condition evaluating to ``True`` where this container evaluates to ``None``, and evaluating to ``False`` elsewhere."""
        return RelationalCondition(
            subject=self._operation_operand, operator="==", target=None
        )

    @final
    def __bool__(self) -> NoReturn:
        raise RuntimeError(
            f"Instances of `{type(self).__name__}` cannot be cast to a boolean. Use a relational operator to create a condition instead.",
        )

    @override
    def __hash__(self) -> int:
        # The public API sometimes requires instances of this class to be used as mapping keys so they must be hashable.
        # However, these keys are only ever iterated upon (i.e. there is no get by key access) so the hash is not important.
        # The ID of the object is thus used, like `object.__hash__()` would do.
        return id(self)

    @final
    def __iter__(self) -> NoReturn:
        # Implementing this method and making it raise an error is required to avoid an endless loop when validating incorrect `AbstractSet`s with Pydantic.
        # For instance, without this, `tt.OriginScope(some_level)` never returns (`tt.OriginScope({some_level})` is the right code).
        # Making this method raise an error prevents Pydantic from calling `__getitem__()` which returns a new `IndexingOperation` instead of an attribute value.
        raise TypeError(f"Instances of {self.__class__.__name__} are not iterable.")

    @final
    def __getitem__(
        self,
        index: HasIdentifier[OtherIdentifierT_co]
        | Operation[OtherIdentifierT_co]
        | slice
        | int
        | Sequence[int],
        /,
    ) -> Operation[IdentifierT_co | OtherIdentifierT_co]:
        return IndexingOperation(
            self._operation_operand,
            index._identifier if isinstance(index, HasIdentifier) else index,
        )

    @override
    # The signature is not compatible with `object.__eq__()` on purpose.
    def __eq__(  # type: ignore[override] # pyright: ignore[reportIncompatibleMethodOverride]
        self,
        other: _ConstantT
        | HasIdentifier[OtherIdentifierT_co]
        | Operation[OtherIdentifierT_co],
        /,
    ) -> RelationalCondition[
        _UnconditionalVariableOperand[IdentifierT_co],
        Literal["=="],
        _ConstantT | OtherIdentifierT_co | Operation[OtherIdentifierT_co],
    ]:
        assert other is not None, "Use `isnull()` instead."
        return RelationalCondition(
            subject=self._operation_operand,
            operator="==",
            target=convert_to_operand(other),
        )

    def __ge__(
        self,
        other: _ConstantT
        | HasIdentifier[OtherIdentifierT_co]
        | Operation[OtherIdentifierT_co],
        /,
    ) -> RelationalCondition[
        _UnconditionalVariableOperand[IdentifierT_co],
        Literal[">="],
        _ConstantT | OtherIdentifierT_co | Operation[OtherIdentifierT_co],
    ]:
        return RelationalCondition(
            subject=self._operation_operand,
            operator=">=",
            target=convert_to_operand(other),
        )

    def __gt__(
        self,
        other: _ConstantT
        | HasIdentifier[OtherIdentifierT_co]
        | Operation[OtherIdentifierT_co],
        /,
    ) -> RelationalCondition[
        _UnconditionalVariableOperand[IdentifierT_co],
        Literal[">"],
        _ConstantT | OtherIdentifierT_co | Operation[OtherIdentifierT_co],
    ]:
        return RelationalCondition(
            subject=self._operation_operand,
            operator=">",
            target=convert_to_operand(other),
        )

    def __le__(
        self,
        other: _ConstantT
        | HasIdentifier[OtherIdentifierT_co]
        | Operation[OtherIdentifierT_co],
        /,
    ) -> RelationalCondition[
        _UnconditionalVariableOperand[IdentifierT_co],
        Literal["<="],
        _ConstantT | OtherIdentifierT_co | Operation[OtherIdentifierT_co],
    ]:
        return RelationalCondition(
            subject=self._operation_operand,
            operator="<=",
            target=convert_to_operand(other),
        )

    def __lt__(
        self,
        other: _ConstantT
        | HasIdentifier[OtherIdentifierT_co]
        | Operation[OtherIdentifierT_co],
        /,
    ) -> RelationalCondition[
        _UnconditionalVariableOperand[IdentifierT_co],
        Literal["<"],
        _ConstantT | OtherIdentifierT_co | Operation[OtherIdentifierT_co],
    ]:
        return RelationalCondition(
            subject=self._operation_operand,
            operator="<",
            target=convert_to_operand(other),
        )

    @override
    # The signature is not compatible with `object.__ne__()` on purpose.
    def __ne__(  # type: ignore[override] # pyright: ignore[reportIncompatibleMethodOverride]
        self,
        other: _ConstantT
        | HasIdentifier[OtherIdentifierT_co]
        | Operation[OtherIdentifierT_co],
        /,
    ) -> RelationalCondition[
        _UnconditionalVariableOperand[IdentifierT_co],
        Literal["!="],
        _ConstantT | OtherIdentifierT_co | Operation[OtherIdentifierT_co],
    ]:
        assert other is not None, "Use `~isnull()` instead."
        return RelationalCondition(
            subject=self._operation_operand,
            operator="!=",
            target=convert_to_operand(other),
        )

    @final
    def __add__(
        self,
        other: Constant
        | HasIdentifier[OtherIdentifierT_co]
        | Operation[OtherIdentifierT_co],
        /,
    ) -> Operation[IdentifierT_co | OtherIdentifierT_co]:
        return NAryArithmeticOperation(
            (self._operation_operand, convert_to_operand(other)),
            "+",
        )

    @final
    def __radd__(
        self,
        other: Constant
        | HasIdentifier[OtherIdentifierT_co]
        | Operation[OtherIdentifierT_co],
        /,
    ) -> Operation[IdentifierT_co | OtherIdentifierT_co]:
        return NAryArithmeticOperation(
            (convert_to_operand(other), self._operation_operand),
            "+",
        )

    @final
    def __floordiv__(
        self,
        other: Constant
        | HasIdentifier[OtherIdentifierT_co]
        | Operation[OtherIdentifierT_co],
        /,
    ) -> Operation[IdentifierT_co | OtherIdentifierT_co]:
        return NAryArithmeticOperation(
            (self._operation_operand, convert_to_operand(other)),
            "//",
        )

    @final
    def __rfloordiv__(
        self,
        other: Constant
        | HasIdentifier[OtherIdentifierT_co]
        | Operation[OtherIdentifierT_co],
        /,
    ) -> Operation[IdentifierT_co | OtherIdentifierT_co]:
        return NAryArithmeticOperation(
            (convert_to_operand(other), self._operation_operand),
            "//",
        )

    @final
    def __mod__(
        self,
        other: Constant
        | HasIdentifier[OtherIdentifierT_co]
        | Operation[OtherIdentifierT_co],
        /,
    ) -> Operation[IdentifierT_co | OtherIdentifierT_co]:
        return NAryArithmeticOperation(
            (self._operation_operand, convert_to_operand(other)),
            "%",
        )

    @final
    def __rmod__(
        self,
        other: Constant
        | HasIdentifier[OtherIdentifierT_co]
        | Operation[OtherIdentifierT_co],
        /,
    ) -> Operation[IdentifierT_co | OtherIdentifierT_co]:
        return NAryArithmeticOperation(
            (convert_to_operand(other), self._operation_operand),
            "%",
        )

    @final
    def __mul__(
        self,
        other: Constant
        | HasIdentifier[OtherIdentifierT_co]
        | Operation[OtherIdentifierT_co],
        /,
    ) -> Operation[IdentifierT_co | OtherIdentifierT_co]:
        return NAryArithmeticOperation(
            (self._operation_operand, convert_to_operand(other)),
            "*",
        )

    @final
    def __rmul__(
        self,
        other: Constant
        | HasIdentifier[OtherIdentifierT_co]
        | Operation[OtherIdentifierT_co],
        /,
    ) -> Operation[IdentifierT_co | OtherIdentifierT_co]:
        return NAryArithmeticOperation(
            (convert_to_operand(other), self._operation_operand),
            "*",
        )

    @final
    def __neg__(
        self,
    ) -> Operation[IdentifierT_co]:
        return UnaryArithmeticOperation(self._operation_operand, "-")

    @final
    def __pow__(
        self,
        other: Constant
        | HasIdentifier[OtherIdentifierT_co]
        | Operation[OtherIdentifierT_co],
        /,
    ) -> Operation[IdentifierT_co | OtherIdentifierT_co]:
        return NAryArithmeticOperation(
            (self._operation_operand, convert_to_operand(other)),
            "**",
        )

    @final
    def __rpow__(
        self,
        other: Constant
        | HasIdentifier[OtherIdentifierT_co]
        | Operation[OtherIdentifierT_co],
        /,
    ) -> Operation[IdentifierT_co | OtherIdentifierT_co]:
        return NAryArithmeticOperation(
            (convert_to_operand(other), self._operation_operand),
            "**",
        )

    @final
    def __sub__(
        self,
        other: Constant
        | HasIdentifier[OtherIdentifierT_co]
        | Operation[OtherIdentifierT_co],
        /,
    ) -> Operation[IdentifierT_co | OtherIdentifierT_co]:
        return NAryArithmeticOperation(
            (self._operation_operand, convert_to_operand(other)),
            "-",
        )

    @final
    def __rsub__(
        self,
        other: Constant
        | HasIdentifier[OtherIdentifierT_co]
        | Operation[OtherIdentifierT_co],
        /,
    ) -> Operation[IdentifierT_co | OtherIdentifierT_co]:
        return NAryArithmeticOperation(
            (convert_to_operand(other), self._operation_operand),
            "-",
        )

    @final
    def __truediv__(
        self,
        other: Constant
        | HasIdentifier[OtherIdentifierT_co]
        | Operation[OtherIdentifierT_co],
        /,
    ) -> Operation[IdentifierT_co | OtherIdentifierT_co]:
        return NAryArithmeticOperation(
            (self._operation_operand, convert_to_operand(other)),
            "/",
        )

    @final
    def __rtruediv__(
        self,
        other: Constant
        | HasIdentifier[OtherIdentifierT_co]
        | Operation[OtherIdentifierT_co],
        /,
    ) -> Operation[IdentifierT_co | OtherIdentifierT_co]:
        return NAryArithmeticOperation(
            (convert_to_operand(other), self._operation_operand),
            "/",
        )


OperandConvertibleBound: TypeAlias = OperandConvertible[Identifier]


class _BaseOperation(ABC):
    """An operation is made out of one or more operands and possibly some other primitive attributes such as strings or numbers.

    This base class' sole purpose is to provide a shared fundation for `Condition` and `Operation`.
    All classes inheriting from `_BaseOperation` must inherit from one of these two classes.
    As such, this class must remain private and not referenced outside this file.
    """

    @property
    @abstractmethod
    def _identifier_types(self) -> frozenset[type[Identifier]]:
        """The set of types of the identifiers used in this operation.

        This is used, for instance, to detect whether an operation is purely column-based and could thus be the input of a UDAF.
        """

    @classmethod
    def _get_identifier_types(
        cls,
        operand: Operand[Identifier] | None,
        /,
    ) -> frozenset[type[Identifier]]:
        match operand:
            case _BaseOperation():
                return operand._identifier_types
            case Identifier():
                return frozenset({type(operand)})
            case None:
                return frozenset()
            case _:
                assert_type(operand, Constant)
                return frozenset()


class Operation(OperandConvertible[IdentifierT_co], _BaseOperation, ABC):
    @property
    @override
    def _operation_operand(self) -> Operation[IdentifierT_co]:
        return self


OperationBound: TypeAlias = Operation[Identifier]

# The following classes can be constructed from any `OperandConvertible` using Python's built-in operators.
# Because overriding these operators requires to implement methods on `OperandConvertible` instantiating the classes below, they all have to be declared in the same file to avoid circular imports.


# Using `BaseModel` instead of `dataclass` because Pydantic does not support validation of generic dataclass attributes.
# See https://github.com/pydantic/pydantic/issues/5803.
# Do not make this class and the ones inheriting from it public until this is fixed because `BaseModel` classes have many methods such as `dump_json()` that should not be part of Atoti's public API.
class BaseCondition(
    BaseModel, _BaseOperation, arbitrary_types_allowed=True, frozen=True
):
    @overload
    def __and__(  # type: ignore[misc]
        self: LogicalConditionLeafOperandT_co,
        other: OtherLogicalConditionLeafOperandT,
        /,
    ) -> LogicalCondition[
        LogicalConditionLeafOperandT_co | OtherLogicalConditionLeafOperandT,
        Literal["&"],
    ]: ...

    @overload
    def __and__(  #  type: ignore[misc]
        self: LogicalConditionLeafOperandT_co,
        other: LogicalCondition[
            OtherLogicalConditionLeafOperandT, OtherLogicalConditionOperatorT
        ],
        /,
    ) -> LogicalCondition[
        LogicalConditionLeafOperandT_co | OtherLogicalConditionLeafOperandT,
        Literal["&"] | OtherLogicalConditionOperatorT,
    ]: ...

    @overload
    def __and__(  #  type: ignore[misc]
        self: LogicalCondition[
            LogicalConditionLeafOperandT_co, LogicalConditionOperatorT_co
        ],
        other: OtherLogicalConditionLeafOperandT,
        /,
    ) -> LogicalCondition[
        LogicalConditionLeafOperandT_co | OtherLogicalConditionLeafOperandT,
        Literal["&"] | LogicalConditionOperatorT_co,
    ]: ...

    @overload
    def __and__(  #  type: ignore[misc]
        self: LogicalCondition[
            LogicalConditionLeafOperandT_co, LogicalConditionOperatorT_co
        ],
        other: LogicalCondition[
            OtherLogicalConditionLeafOperandT, OtherLogicalConditionOperatorT
        ],
        /,
    ) -> LogicalCondition[
        LogicalConditionLeafOperandT_co | OtherLogicalConditionLeafOperandT,
        Literal["&"] | LogicalConditionOperatorT_co | OtherLogicalConditionOperatorT,
    ]: ...

    def __and__(
        self,
        other: ConditionBound,
        /,
    ) -> LogicalConditionBound:
        assert isinstance(self, Condition)
        return _combine(self, "&", other)

    @final
    def __bool__(self) -> NoReturn:
        raise RuntimeError(
            "Conditions cannot be cast to a boolean since they are only evaluated during query execution. To combine conditions, use the bitwise `&`, `|`, or `~` operators.",
        )

    @abstractmethod
    def __invert__(self) -> ConditionBound: ...

    @overload
    def __or__(  #  type: ignore[misc]
        self: LogicalConditionLeafOperandT_co,
        other: OtherLogicalConditionLeafOperandT,
        /,
    ) -> LogicalCondition[
        LogicalConditionLeafOperandT_co | OtherLogicalConditionLeafOperandT,
        Literal["|"],
    ]: ...

    @overload
    def __or__(  #  type: ignore[misc]
        self: LogicalConditionLeafOperandT_co,
        other: LogicalCondition[
            OtherLogicalConditionLeafOperandT, OtherLogicalConditionOperatorT
        ],
        /,
    ) -> LogicalCondition[
        LogicalConditionLeafOperandT_co | OtherLogicalConditionLeafOperandT,
        Literal["|"] | OtherLogicalConditionOperatorT,
    ]: ...

    @overload
    def __or__(  #  type: ignore[misc]
        self: LogicalCondition[
            LogicalConditionLeafOperandT_co, LogicalConditionOperatorT_co
        ],
        other: OtherLogicalConditionLeafOperandT,
        /,
    ) -> LogicalCondition[
        LogicalConditionLeafOperandT_co | OtherLogicalConditionLeafOperandT,
        Literal["|"] | LogicalConditionOperatorT_co,
    ]: ...

    @overload
    def __or__(  #  type: ignore[misc]
        self: LogicalCondition[
            LogicalConditionLeafOperandT_co, LogicalConditionOperatorT_co
        ],
        other: LogicalCondition[
            OtherLogicalConditionLeafOperandT, OtherLogicalConditionOperatorT
        ],
        /,
    ) -> LogicalCondition[
        LogicalConditionLeafOperandT_co | OtherLogicalConditionLeafOperandT,
        Literal["|"] | LogicalConditionOperatorT_co | OtherLogicalConditionOperatorT,
    ]: ...

    def __or__(
        self,
        other: ConditionBound,
        /,
    ) -> LogicalConditionBound:
        assert isinstance(self, Condition)
        return _combine(self, "|", other)

    @override
    def __str__(self) -> str:
        return repr(self)

    @final
    def __xor__(self, other: ConditionBound, /) -> NoReturn:
        raise RuntimeError(
            "Conditions cannot be `xor`ed.",
        )


def _validate_constant_target(target: _ConstantT, /) -> _ConstantT:
    if isinstance(target, float) and math.isnan(target):
        raise ValueError("Use the `isnan()` method to compare against NaN.")

    return target


MembershipConditionOperatorT_co = TypeVar(
    "MembershipConditionOperatorT_co", bound=MembershipOperator, covariant=True
)


@final
class HierarchyMembershipCondition(
    BaseCondition, Generic[MembershipConditionOperatorT_co, ScalarT_co], frozen=True
):
    subject: HierarchyIdentifier
    operator: MembershipConditionOperatorT_co
    member_paths: Annotated[
        AbstractSet[
            Annotated[
                tuple[
                    Annotated[
                        ScalarT_co,
                        AfterValidator(_validate_constant_target),
                    ],
                    ...,
                ],
                Field(min_length=1),
            ]
        ],
        Field(min_length=1),
    ]
    level_names: Annotated[FrozenSequence[LevelName], Field(min_length=1, repr=False)]

    @property
    @override
    def _identifier_types(self) -> frozenset[type[Identifier]]:
        return frozenset({type(self.subject)})

    # Not a `@property` to be able to use `@overload`
    @overload
    def _logical_relational(
        self: HierarchyMembershipCondition[Literal["in"], ScalarT_co],
        /,
    ) -> (
        RelationalCondition[LevelIdentifier, Literal["=="], Scalar | None]
        | LogicalCondition[
            RelationalCondition[LevelIdentifier, Literal["=="], Scalar | None],
            LogicalOperator,
        ]
    ): ...

    @overload
    def _logical_relational(
        self: HierarchyMembershipCondition[Literal["not in"], ScalarT_co],
        /,
    ) -> (
        RelationalCondition[LevelIdentifier, Literal["!="], Scalar | None]
        | LogicalCondition[
            RelationalCondition[LevelIdentifier, Literal["!="], Scalar | None],
            LogicalOperator,
        ]
    ): ...

    @overload
    def _logical_relational(
        self, /
    ) -> (
        RelationalCondition[LevelIdentifier, EqualityOperator, Scalar | None]
        | LogicalCondition[
            RelationalCondition[LevelIdentifier, EqualityOperator, Scalar | None],
            LogicalOperator,
        ]
    ): ...

    def _logical_relational(
        self, /
    ) -> (
        RelationalCondition[LevelIdentifier, EqualityOperator, Scalar | None]
        | LogicalCondition[
            RelationalCondition[LevelIdentifier, EqualityOperator, Scalar | None],
            LogicalOperator,
        ]
    ):
        from .condition_from_dnf import (  # pylint: disable=nested-import
            condition_from_dnf,
        )

        match self.operator:
            case "in":
                return condition_from_dnf(
                    [
                        [
                            RelationalCondition(
                                subject=LevelIdentifier(self.subject, level_name),
                                operator="==",
                                target=value,
                            )
                            for value, level_name in zip(
                                member_path, self.level_names, strict=False
                            )
                        ]
                        for member_path in self._sorted_member_paths
                    ]
                )
            case "not in":
                return cast(
                    RelationalCondition[
                        LevelIdentifier,
                        EqualityOperator,
                        ScalarT_co | None,
                    ]
                    | LogicalCondition[
                        RelationalCondition[
                            LevelIdentifier,
                            EqualityOperator,
                            ScalarT_co | None,
                        ],
                        LogicalOperator,
                    ],
                    ~((~self)._logical_relational()),
                )

    @cached_property
    def _sorted_member_paths(
        self,
    ) -> tuple[tuple[ScalarT_co, ...], ...]:
        return tuple(sorted(self.member_paths))

    @overload
    def __invert__(
        self: HierarchyMembershipCondition[Literal["in"], ScalarT_co],
        /,
    ) -> HierarchyMembershipCondition[Literal["not in"], ScalarT_co]: ...

    @overload
    def __invert__(
        self: HierarchyMembershipCondition[Literal["not in"], ScalarT_co],
        /,
    ) -> HierarchyMembershipCondition[Literal["in"], ScalarT_co]: ...

    @overload
    def __invert__(self, /) -> HierarchyMembershipConditionBound: ...

    @override
    def __invert__(self, /) -> HierarchyMembershipConditionBound:
        return HierarchyMembershipCondition(
            subject=self.subject,
            operator=invert_membership_operator(self.operator),
            member_paths=self.member_paths,
            level_names=self.level_names,
        )

    @override
    def __repr__(self) -> str:
        result = f"{self.subject}.isin{self._sorted_member_paths}"

        match self.operator:
            case "in":
                return result
            case "not in":
                return f"~{result}"


HierarchyMembershipConditionBound: TypeAlias = HierarchyMembershipCondition[
    MembershipOperator, Scalar
]


MembershipConditionSubjectBound: TypeAlias = Identifier
MembershipConditionSubjectT_co = TypeVar(
    "MembershipConditionSubjectT_co",
    bound=MembershipConditionSubjectBound,
    covariant=True,
)


MembershipConditionElementBound: TypeAlias = Constant | None
MembershipConditionElementT_co = TypeVar(
    "MembershipConditionElementT_co",
    bound=MembershipConditionElementBound,
    covariant=True,
)


def _validate_element(
    element: MembershipConditionElementT_co,  # type: ignore[misc]
    /,
) -> MembershipConditionElementT_co:
    return element if element is None else _validate_constant_target(element)


_ScalarOnlyIdentifier: TypeAlias = HierarchyIdentifier | LevelIdentifier


@final
class MembershipCondition(
    BaseCondition,
    Generic[
        MembershipConditionSubjectT_co,
        MembershipConditionOperatorT_co,
        MembershipConditionElementT_co,
    ],
    frozen=True,
):
    subject: MembershipConditionSubjectT_co
    operator: MembershipConditionOperatorT_co
    elements: Annotated[
        AbstractSet[
            Annotated[MembershipConditionElementT_co, AfterValidator(_validate_element)]
        ],
        Field(min_length=2),
    ]

    @overload
    @classmethod
    def of(
        cls,
        *,
        subject: MembershipConditionSubjectT_co,  # type: ignore[misc] # pyright: ignore[reportGeneralTypeIssues]
        operator: Literal["in"],
        elements: AbstractSet[MembershipConditionElementT_co],
    ) -> (
        MembershipCondition[
            MembershipConditionSubjectT_co,
            Literal["in"],
            MembershipConditionElementT_co,
        ]
        | RelationalCondition[
            MembershipConditionSubjectT_co,
            Literal["=="],
            MembershipConditionElementT_co,
        ]
    ): ...

    @overload
    @classmethod
    def of(
        cls,
        *,
        subject: MembershipConditionSubjectT_co,  # type: ignore[misc] # pyright: ignore[reportGeneralTypeIssues]
        operator: Literal["not in"],
        elements: AbstractSet[MembershipConditionElementT_co],
    ) -> (
        MembershipCondition[
            MembershipConditionSubjectT_co,
            Literal["not in"],
            MembershipConditionElementT_co,
        ]
        | RelationalCondition[
            MembershipConditionSubjectT_co,
            Literal["!="],
            MembershipConditionElementT_co,
        ]
    ): ...

    @overload
    @classmethod
    def of(
        cls,
        *,
        subject: MembershipConditionSubjectT_co,  # type: ignore[misc] # pyright: ignore[reportGeneralTypeIssues]
        operator: MembershipConditionOperatorT_co,  # type: ignore[misc] # pyright: ignore[reportGeneralTypeIssues]
        elements: AbstractSet[MembershipConditionElementT_co],
    ) -> (
        MembershipCondition[
            MembershipConditionSubjectT_co,
            MembershipConditionOperatorT_co,
            MembershipConditionElementT_co,
        ]
        | RelationalCondition[
            MembershipConditionSubjectT_co,
            EqualityOperator,
            MembershipConditionElementT_co,
        ]
    ): ...

    @classmethod  # type: ignore[misc]
    def of(  # pyright: ignore[reportInconsistentOverload]
        cls,
        *,
        subject: MembershipConditionSubjectT_co,  # type: ignore[misc] # pyright: ignore[reportGeneralTypeIssues]
        operator: MembershipConditionOperatorT_co,  # type: ignore[misc] # pyright: ignore[reportGeneralTypeIssues]
        elements: AbstractSet[MembershipConditionElementT_co],
    ) -> (
        MembershipCondition[
            MembershipConditionSubjectT_co,
            MembershipConditionOperatorT_co,
            MembershipConditionElementT_co,
        ]
        | RelationalCondition[
            MembershipConditionSubjectT_co,
            EqualityOperator,
            MembershipConditionElementT_co,
        ]
    ):
        if len(elements) == 1:
            match operator:
                case "in":
                    relational_operator: EqualityOperator = "=="
                case "not in":
                    relational_operator = "!="
            return RelationalCondition(
                subject=subject,
                operator=relational_operator,
                target=next(iter(elements)),
            )

        return cls(subject=subject, operator=operator, elements=elements)

    @model_validator(mode="after")  # type: ignore[misc]
    def _validate(self) -> Self:
        if isinstance(self.subject, HierarchyIdentifier) and None in self.elements:
            raise ValueError(
                f"Subject `{self.subject}` is a hierarchy and will thus always be expressed so the `None` element will never match."
            )

        if isinstance(self.subject, _ScalarOnlyIdentifier):
            invalid_elements = {
                element
                for element in self.elements
                if element is not None and not is_scalar(element)
            }
            if invalid_elements:
                raise ValueError(
                    f"Subject `{self.subject}` only supports scalar elements but also got `{invalid_elements}`."
                )

        return self

    @property
    @override
    def _identifier_types(self) -> frozenset[type[Identifier]]:
        return frozenset({type(self.subject)})

    # Not a `@property` to be able to use `@overload`
    @overload
    def _logical_relational(
        self: MembershipCondition[
            MembershipConditionSubjectT_co,
            Literal["in"],
            MembershipConditionElementT_co,
        ],
        /,
    ) -> (
        RelationalCondition[
            MembershipConditionSubjectT_co,
            Literal["=="],
            MembershipConditionElementT_co,
        ]
        | LogicalCondition[
            RelationalCondition[
                MembershipConditionSubjectT_co,
                Literal["=="],
                MembershipConditionElementT_co,
            ],
            Literal["|"],
        ]
    ): ...

    @overload
    def _logical_relational(
        self: MembershipCondition[
            MembershipConditionSubjectT_co,
            Literal["not in"],
            MembershipConditionElementT_co,
        ],
        /,
    ) -> (
        RelationalCondition[
            MembershipConditionSubjectT_co,
            Literal["!="],
            MembershipConditionElementT_co,
        ]
        | LogicalCondition[
            RelationalCondition[
                MembershipConditionSubjectT_co,
                Literal["!="],
                MembershipConditionElementT_co,
            ],
            Literal["&"],
        ]
    ): ...

    @overload
    def _logical_relational(
        self: MembershipCondition[
            MembershipConditionSubjectT_co,
            MembershipOperator,
            MembershipConditionElementT_co,
        ],
        /,
    ) -> (
        RelationalCondition[
            MembershipConditionSubjectT_co,
            EqualityOperator,
            MembershipConditionElementT_co,
        ]
        | LogicalCondition[
            RelationalCondition[
                MembershipConditionSubjectT_co,
                EqualityOperator,
                MembershipConditionElementT_co,
            ],
            LogicalOperator,
        ]
    ): ...

    def _logical_relational(
        self: MembershipCondition[
            MembershipConditionSubjectT_co,
            MembershipOperator,
            MembershipConditionElementT_co,
        ],
        /,
    ) -> (
        RelationalCondition[
            MembershipConditionSubjectT_co,
            EqualityOperator,
            MembershipConditionElementT_co,
        ]
        | LogicalCondition[
            RelationalCondition[
                MembershipConditionSubjectT_co,
                EqualityOperator,
                MembershipConditionElementT_co,
            ],
            LogicalOperator,
        ]
    ):
        from .condition_from_dnf import (  # pylint: disable=nested-import
            condition_from_dnf,
        )

        match self.operator:
            case "in":
                return condition_from_dnf(
                    tuple(
                        (
                            RelationalCondition(
                                subject=self.subject, operator="==", target=element
                            ),
                        )
                        for element in self._sorted_elements
                    )
                )
            case "not in":
                return cast(
                    RelationalCondition[
                        MembershipConditionSubjectT_co,
                        EqualityOperator,
                        MembershipConditionElementT_co,
                    ]
                    | LogicalCondition[
                        RelationalCondition[
                            MembershipConditionSubjectT_co,
                            EqualityOperator,
                            MembershipConditionElementT_co,
                        ],
                        LogicalOperator,
                    ],
                    ~((~self)._logical_relational()),
                )

    @cached_property
    def _sorted_elements(self) -> tuple[MembershipConditionElementT_co, ...]:
        return (
            # Collections containing `None` cannot be sorted.
            # If `None` is in the elements it's added at the head of the tuple.
            # The remaining non-`None` elements are sorted and inserted after.
            *([None] if None in self.elements else []),  # type: ignore[arg-type] # pyright: ignore[reportReturnType]
            *sorted(element for element in self.elements if element is not None),
        )

    @overload
    def __invert__(
        self: MembershipCondition[
            MembershipConditionSubjectT_co,
            Literal["in"],
            MembershipConditionElementT_co,
        ],
        /,
    ) -> MembershipCondition[
        MembershipConditionSubjectT_co,
        Literal["not in"],
        MembershipConditionElementT_co,
    ]: ...

    @overload
    def __invert__(
        self: MembershipCondition[
            MembershipConditionSubjectT_co,
            Literal["not in"],
            MembershipConditionElementT_co,
        ],
        /,
    ) -> MembershipCondition[
        MembershipConditionSubjectT_co, Literal["in"], MembershipConditionElementT_co
    ]: ...

    @overload
    def __invert__(
        self: MembershipCondition[
            MembershipConditionSubjectT_co,
            MembershipOperator,
            MembershipConditionElementT_co,
        ],
        /,
    ) -> MembershipCondition[
        MembershipConditionSubjectT_co,
        MembershipOperator,
        MembershipConditionElementT_co,
    ]: ...

    @override
    def __invert__(self, /) -> MembershipConditionBound:
        return MembershipCondition(
            subject=self.subject,
            operator=invert_membership_operator(self.operator),
            elements=self.elements,
        )

    @override
    def __repr__(self) -> str:
        result = f"{self.subject}.isin{self._sorted_elements}"

        match self.operator:
            case "in":
                return result
            case "not in":
                return f"~{result}"


MembershipConditionBound: TypeAlias = MembershipCondition[
    MembershipConditionSubjectBound, MembershipOperator, MembershipConditionElementBound
]

RelationalConditionSubjectBound: TypeAlias = Identifier | OperationBound
RelationalConditionSubjectT_co = TypeVar(
    "RelationalConditionSubjectT_co",
    bound=RelationalConditionSubjectBound,
    covariant=True,
)

RelationalConditionOperatorT_co = TypeVar(
    "RelationalConditionOperatorT_co",
    bound=RelationalOperator,
    covariant=True,
)

RelationalConditionTargetBound: TypeAlias = (
    Constant | Identifier | OperationBound | None
)
RelationalConditionTargetT_co = TypeVar(
    "RelationalConditionTargetT_co",
    bound=RelationalConditionTargetBound,
    covariant=True,
)


def _validate_relational_condition_target(
    target: RelationalConditionTargetT_co,  # type: ignore[misc]
    /,
) -> RelationalConditionTargetT_co:
    match target:
        case Identifier() | Operation() | None:
            return target  # type: ignore[return-value] # pyright: ignore[reportReturnType]
        case _:
            return _validate_constant_target(target)


@final
class RelationalCondition(
    BaseCondition,
    Generic[
        RelationalConditionSubjectT_co,
        RelationalConditionOperatorT_co,
        RelationalConditionTargetT_co,
    ],
    frozen=True,
):
    subject: RelationalConditionSubjectT_co
    operator: RelationalConditionOperatorT_co
    target: Annotated[
        RelationalConditionTargetT_co,
        AfterValidator(_validate_relational_condition_target),
    ]

    @model_validator(mode="after")  # type: ignore[misc]
    def _validate(self) -> Self:
        if isinstance(self.subject, HierarchyIdentifier) and self.target is None:
            raise ValueError(
                f"Subject `{self.subject}` is a hierarchy and will thus always be expressed so the `None` target will never match."
            )

        if (
            isinstance(self.subject, _ScalarOnlyIdentifier)
            and not isinstance(self.target, Identifier | Operation | None)
            and not is_scalar(self.target)
        ):
            raise ValueError(
                f"Subject `{self.subject}` only suports scalar targets but got `{self.target}`."
            )

        if (isinstance(self.subject, HierarchyIdentifier) or self.target is None) and (
            self.operator != "==" and self.operator != "!="
        ):
            raise ValueError(
                f"Subject `{self.subject}` cannot be compared to target `{self.target}` target with operator `{self.operator}`."
            )

        return self

    @property
    @override
    def _identifier_types(self) -> frozenset[type[Identifier]]:
        return frozenset(
            chain.from_iterable(
                self._get_identifier_types(operand)
                for operand in [self.subject, self.target]
            ),
        )

    @overload
    def __invert__(
        self: RelationalCondition[
            RelationalConditionSubjectT_co, Literal["=="], RelationalConditionTargetT_co
        ],
        /,
    ) -> RelationalCondition[
        RelationalConditionSubjectT_co, Literal["!="], RelationalConditionTargetT_co
    ]: ...

    @overload
    def __invert__(
        self: RelationalCondition[
            RelationalConditionSubjectT_co, Literal[">="], RelationalConditionTargetT_co
        ],
        /,
    ) -> RelationalCondition[
        RelationalConditionSubjectT_co, Literal["<"], RelationalConditionTargetT_co
    ]: ...

    @overload
    def __invert__(
        self: RelationalCondition[
            RelationalConditionSubjectT_co, Literal[">"], RelationalConditionTargetT_co
        ],
        /,
    ) -> RelationalCondition[
        RelationalConditionSubjectT_co, Literal["<="], RelationalConditionTargetT_co
    ]: ...

    @overload
    def __invert__(
        self: RelationalCondition[
            RelationalConditionSubjectT_co, Literal["<="], RelationalConditionTargetT_co
        ],
        /,
    ) -> RelationalCondition[
        RelationalConditionSubjectT_co, Literal[">"], RelationalConditionTargetT_co
    ]: ...

    @overload
    def __invert__(
        self: RelationalCondition[
            RelationalConditionSubjectT_co, Literal["<"], RelationalConditionTargetT_co
        ],
        /,
    ) -> RelationalCondition[
        RelationalConditionSubjectT_co, Literal[">="], RelationalConditionTargetT_co
    ]: ...

    @overload
    def __invert__(
        self: RelationalCondition[
            RelationalConditionSubjectT_co, Literal["!="], RelationalConditionTargetT_co
        ],
        /,
    ) -> RelationalCondition[
        RelationalConditionSubjectT_co, Literal["=="], RelationalConditionTargetT_co
    ]: ...

    @overload
    def __invert__(
        self: RelationalCondition[
            RelationalConditionSubjectT_co,
            RelationalOperator,
            RelationalConditionTargetT_co,
        ],
        /,
    ) -> RelationalCondition[
        RelationalConditionSubjectT_co,
        RelationalOperator,
        RelationalConditionTargetT_co,
    ]: ...

    @override
    def __invert__(self, /) -> RelationalConditionBound:
        return RelationalCondition(
            subject=self.subject,
            operator=invert_relational_operator(self.operator),
            target=self.target,
        )

    @override
    def __repr__(self) -> str:
        if self.target is None:
            assert self.operator == "==" or self.operator == "!="

            result = f"{self.subject}.isnull()"
            match self.operator:
                case "==":
                    return result
                case "!=":
                    return f"~{result}"

        return f"{self.subject} {self.operator} {self.target!r}"


RelationalConditionBound: TypeAlias = RelationalCondition[
    RelationalConditionSubjectBound, RelationalOperator, RelationalConditionTargetBound
]

LogicalConditionLeafOperandBound: TypeAlias = (
    HierarchyMembershipConditionBound
    | MembershipConditionBound
    | RelationalConditionBound
)
LogicalConditionLeafOperandT_co = TypeVar(
    "LogicalConditionLeafOperandT_co",
    bound=LogicalConditionLeafOperandBound,
    covariant=True,
)

LogicalConditionOperatorT_co = TypeVar(
    "LogicalConditionOperatorT_co", bound=LogicalOperator, covariant=True
)


@final
class LogicalCondition(
    BaseCondition,
    Generic[
        LogicalConditionLeafOperandT_co,
        LogicalConditionOperatorT_co,
    ],
    frozen=True,
):
    # See https://github.com/pydantic/pydantic/issues/7905#issuecomment-1783302168.
    operands: SerializeAsAny[
        Annotated[
            # Using a sequence instead of a set because the order can be significant (e.g. the order of MDX filters can matter).
            tuple[
                LogicalConditionLeafOperandT_co
                | LogicalCondition[
                    LogicalConditionLeafOperandT_co, LogicalConditionOperatorT_co
                ],
                ...,
            ],
            Field(min_length=2),
        ]
    ]
    operator: LogicalConditionOperatorT_co

    @model_validator(mode="after")  # type: ignore[misc]
    def _validate_flatness(self) -> Self:
        needlessly_nested_operand = next(
            (
                operand
                for operand in self.operands
                if isinstance(operand, self.__class__)
                and operand.operator == self.operator
            ),
            None,
        )
        if needlessly_nested_operand is not None:
            raise ValueError(
                f"This condition and its operand {needlessly_nested_operand} must be flattened since they both use the `{self.operator}` operator."
            )
        return self

    @property
    @override
    def _identifier_types(self) -> frozenset[type[Identifier]]:
        return frozenset(
            chain.from_iterable(operand._identifier_types for operand in self.operands),
        )

    @overload
    def __invert__(
        self: LogicalCondition[
            HierarchyMembershipConditionBound,
            LogicalOperator,
        ],
        /,
    ) -> LogicalCondition[
        HierarchyMembershipConditionBound,
        LogicalOperator,
    ]: ...

    @overload
    def __invert__(
        self: LogicalCondition[
            MembershipCondition[
                MembershipConditionSubjectT_co,
                MembershipOperator,
                MembershipConditionElementT_co,
            ],
            LogicalOperator,
        ],
        /,
    ) -> LogicalCondition[
        MembershipCondition[
            MembershipConditionSubjectT_co,
            MembershipOperator,
            MembershipConditionElementT_co,
        ],
        LogicalOperator,
    ]: ...

    @overload
    def __invert__(  # type: ignore[overload-overlap] # pyright: ignore[reportOverlappingOverload]
        self: LogicalCondition[
            HierarchyMembershipConditionBound
            | MembershipCondition[
                MembershipConditionSubjectT_co,
                MembershipOperator,
                MembershipConditionElementT_co,
            ],
            LogicalOperator,
        ],
        /,
    ) -> LogicalCondition[
        HierarchyMembershipConditionBound
        | MembershipCondition[
            MembershipConditionSubjectT_co,
            MembershipOperator,
            MembershipConditionElementT_co,
        ],
        LogicalOperator,
    ]: ...

    @overload
    def __invert__(
        self: LogicalCondition[
            RelationalCondition[
                RelationalConditionSubjectT_co,
                RelationalOperator,
                RelationalConditionTargetT_co,
            ],
            LogicalOperator,
        ],
        /,
    ) -> LogicalCondition[
        RelationalCondition[
            RelationalConditionSubjectT_co,
            RelationalOperator,
            RelationalConditionTargetT_co,
        ],
        LogicalOperator,
    ]: ...

    @overload
    def __invert__(  # type: ignore[overload-overlap]
        self: LogicalCondition[
            HierarchyMembershipConditionBound
            | RelationalCondition[
                RelationalConditionSubjectT_co,
                RelationalOperator,
                RelationalConditionTargetT_co,
            ],
            LogicalOperator,
        ],
        /,
    ) -> LogicalCondition[
        HierarchyMembershipConditionBound
        | RelationalCondition[
            RelationalConditionSubjectT_co,
            RelationalOperator,
            RelationalConditionTargetT_co,
        ],
        LogicalOperator,
    ]: ...

    @overload
    def __invert__(
        self: LogicalCondition[
            MembershipCondition[
                MembershipConditionSubjectT_co,
                MembershipOperator,
                MembershipConditionElementT_co,
            ]
            | RelationalCondition[
                RelationalConditionSubjectT_co,
                RelationalOperator,
                RelationalConditionTargetT_co,
            ],
            LogicalOperator,
        ],
        /,
    ) -> LogicalCondition[
        MembershipCondition[
            MembershipConditionSubjectT_co,
            MembershipOperator,
            MembershipConditionElementT_co,
        ]
        | RelationalCondition[
            RelationalConditionSubjectT_co,
            RelationalOperator,
            RelationalConditionTargetT_co,
        ],
        LogicalOperator,
    ]: ...

    @overload
    def __invert__(
        self: LogicalCondition[
            HierarchyMembershipConditionBound
            | MembershipCondition[
                MembershipConditionSubjectT_co,
                MembershipOperator,
                MembershipConditionElementT_co,
            ]
            | RelationalCondition[
                RelationalConditionSubjectT_co,
                RelationalOperator,
                RelationalConditionTargetT_co,
            ],
            LogicalOperator,
        ],
        /,
    ) -> LogicalCondition[
        HierarchyMembershipConditionBound
        | MembershipCondition[
            MembershipConditionSubjectT_co,
            MembershipOperator,
            MembershipConditionElementT_co,
        ]
        | RelationalCondition[
            RelationalConditionSubjectT_co,
            RelationalOperator,
            RelationalConditionTargetT_co,
        ],
        LogicalOperator,
    ]: ...

    @override
    def __invert__(self, /) -> LogicalConditionBound:
        match self.operator:
            case "&":
                operator: LogicalOperator = "|"
            case "|":
                operator = "&"

        return LogicalCondition(
            operands=tuple(~operand for operand in self.operands),
            operator=operator,
        )

    @override
    def __repr__(self) -> str:
        def _repr_operand(operand: ConditionBound, /) -> str:
            match operand:
                case LogicalCondition():
                    return f"({operand})"
                case RelationalCondition():
                    return str(operand) if operand.target is None else f"({operand})"
                case HierarchyMembershipCondition() | MembershipCondition():
                    return str(operand)

        return f" {self.operator} ".join(
            _repr_operand(operand) for operand in self.operands
        )


LogicalConditionBound: TypeAlias = LogicalCondition[
    LogicalConditionLeafOperandBound, LogicalOperator
]


Condition = (
    HierarchyMembershipCondition,
    LogicalCondition,
    MembershipCondition,
    RelationalCondition,
)
ConditionBound: TypeAlias = LogicalConditionLeafOperandBound | LogicalConditionBound


OtherLogicalConditionLeafOperandT = TypeVar(
    "OtherLogicalConditionLeafOperandT",
    bound=LogicalConditionLeafOperandBound,
)
OtherLogicalConditionOperatorT = TypeVar(
    "OtherLogicalConditionOperatorT",
    bound=LogicalOperator,
)


def _combine(
    left: LogicalConditionLeafOperandT_co
    | LogicalCondition[LogicalConditionLeafOperandT_co, LogicalConditionOperatorT_co],
    operator: OtherLogicalConditionOperatorT,
    right: LogicalConditionLeafOperandT_co
    | LogicalCondition[LogicalConditionLeafOperandT_co, LogicalConditionOperatorT_co],
    /,
) -> LogicalCondition[
    LogicalConditionLeafOperandT_co,
    LogicalConditionOperatorT_co | OtherLogicalConditionOperatorT,
]:
    if isinstance(left, LogicalCondition) and left.operator == operator:
        if isinstance(right, LogicalCondition) and right.operator == operator:
            return LogicalCondition(
                operands=(*left.operands, *right.operands), operator=operator
            )
        return LogicalCondition(operands=(*left.operands, right), operator=operator)
    if isinstance(right, LogicalCondition) and right.operator == operator:
        return LogicalCondition(operands=(left, *right.operands), operator=operator)
    return LogicalCondition(operands=(left, right), operator=operator)


@final
@_dataclass(eq=False, frozen=True)
class IndexingOperation(Operation[IdentifierT_co]):
    operand: _UnconditionalVariableOperand[IdentifierT_co]
    index: (
        slice | int | FrozenSequence[int] | IdentifierT_co | Operation[IdentifierT_co]
    )
    _: KW_ONLY

    @property
    @override
    def _identifier_types(self) -> frozenset[type[Identifier]]:
        return self._get_identifier_types(self.operand) | (
            frozenset()
            if isinstance(self.index, int | Sequence | slice)
            else self._get_identifier_types(self.index)
        )

    @override
    def __repr__(self) -> str:
        return f"{self.operand}[{self.index}]"


def _repr_operand(operand: _UnconditionalOperand[Identifier], /) -> str:
    operand_representation = repr(operand)
    operation_is_function_call_result = not isinstance(
        operand,
        (
            *Condition,
            IndexingOperation,
            NAryArithmeticOperation,
            UnaryArithmeticOperation,
        ),
    )
    return (
        operand_representation
        if operation_is_function_call_result
        else f"({operand_representation})"
    )


@final
@dataclass(config=_PYDANTIC_CONFIG, eq=False, frozen=True)
class NAryArithmeticOperation(Operation[IdentifierT_co]):
    operands: FrozenSequence[_UnconditionalOperand[IdentifierT_co]]
    """The operands of the operation.

    To keep operation ASTs compact, this can contain more than 2 elements if the operator is associative.

    For example, `+` and `*` are binary operators but they are associative so `operands` can have more than 2 elements.
    """
    operator: NAryArithmeticOperator
    _: KW_ONLY

    @property
    @override
    def _identifier_types(self) -> frozenset[type[Identifier]]:
        return frozenset(
            chain.from_iterable(
                self._get_identifier_types(operand) for operand in self.operands
            )
        )

    @override
    def __repr__(self) -> str:
        return self.operator.join(_repr_operand(operand) for operand in self.operands)


@final
@dataclass(config=_PYDANTIC_CONFIG, eq=False, frozen=True)
class UnaryArithmeticOperation(Operation[IdentifierT_co]):
    operand: _UnconditionalOperand[IdentifierT_co]
    operator: UnaryArithmeticOperator
    _: KW_ONLY

    @property
    @override
    def _identifier_types(self) -> frozenset[type[Identifier]]:
        return frozenset(self._get_identifier_types(self.operand))

    @override
    def __repr__(self) -> str:
        return f"{self.operator}{_repr_operand(self.operand)}"


_UnconditionalVariableOperand: TypeAlias = IdentifierT_co | Operation[IdentifierT_co]
_UnconditionalOperand: TypeAlias = (
    Constant | _UnconditionalVariableOperand[IdentifierT_co]
)


_OperandLeafCondition: TypeAlias = RelationalCondition[
    _UnconditionalVariableOperand[IdentifierT_co],
    RelationalOperator,
    _UnconditionalOperand[IdentifierT_co] | None,
]
_OperandLeafCondition.__parameters__ = (IdentifierT_co,)  # type: ignore[attr-defined] # pyright: ignore[reportAttributeAccessIssue]
_OperandLogicalCondition: TypeAlias = LogicalCondition[
    _OperandLeafCondition[IdentifierT_co],
    LogicalOperator,
]
_OperandLogicalCondition.__parameters__ = (IdentifierT_co,)  # type: ignore[attr-defined] # pyright: ignore[reportAttributeAccessIssue]
OperandCondition: TypeAlias = Union[  # noqa: UP007
    _OperandLeafCondition[IdentifierT_co], _OperandLogicalCondition[IdentifierT_co]
]
OperandCondition.__dict__["__parameters__"] = (IdentifierT_co,)


_VariableOperand: TypeAlias = (
    _UnconditionalVariableOperand[IdentifierT_co] | OperandCondition[IdentifierT_co]
)
Operand: TypeAlias = Constant | _VariableOperand[IdentifierT_co]
