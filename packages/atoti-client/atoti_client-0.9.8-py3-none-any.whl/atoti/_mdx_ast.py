# Adapted from:
# - https://github.com/activeviam/atoti-ui/blob/eb113a9164ee18443d35ce3bb9e09111c76c4db2/packages/mdx/src/mdx.types.ts.
# - https://github.com/activeviam/atoti-ui/blob/eb113a9164ee18443d35ce3bb9e09111c76c4db2/packages/mdx/src/stringify.ts.

from __future__ import annotations

from abc import ABC
from collections.abc import Sequence
from dataclasses import field
from typing import Annotated, Generic, Literal, TypeAlias, TypeVar, final

from pydantic import AliasChoices, ConfigDict, Discriminator, Field
from pydantic.dataclasses import dataclass
from typing_extensions import Self, override

from ._collections import FrozenSequence
from ._identification import (
    MEASURES_HIERARCHY_IDENTIFIER,
    CubeName,
    DimensionName,
    HierarchyIdentifier,
    HierarchyName,
    LevelIdentifier,
    LevelName,
    MeasureIdentifier,
    MeasureName,
)
from ._pydantic import (
    PYDANTIC_CONFIG as __PYDANTIC_CONFIG,
    create_camel_case_alias_generator,
)

_PYDANTIC_CONFIG: ConfigDict = {
    **__PYDANTIC_CONFIG,
    "alias_generator": create_camel_case_alias_generator(
        force_aliased_attribute_names={"element_type"},
    ),
    "arbitrary_types_allowed": False,
    "extra": "ignore",
}


def _escape(value: str, /) -> str:
    return value.replace("]", "]]")


def _quote(*values: str) -> str:
    return ".".join(f"[{_escape(value)}]" for value in values)


@final
@dataclass(config=_PYDANTIC_CONFIG, frozen=True, kw_only=True)
class MdxLiteral:
    element_type: Literal["Literal"] = field(default="Literal", init=False, repr=False)
    type: Literal["KEYWORD", "SCALAR", "STRING"]
    value: str

    @classmethod
    def keyword(cls, value: str, /) -> Self:
        return cls(type="KEYWORD", value=value)

    @classmethod
    def scalar(cls, value: str, /) -> Self:
        return cls(type="SCALAR", value=value)

    @classmethod
    def string(cls, value: str, /) -> Self:
        return cls(type="STRING", value=value)

    @override
    def __str__(self) -> str:
        match self.type:
            case "KEYWORD" | "SCALAR":
                return self.value
            case "STRING":
                return f'"{self.value}"'


@final
@dataclass(config=_PYDANTIC_CONFIG, frozen=True, kw_only=True)
class MdxIdentifier:
    element_type: Literal["Identifier"] = field(
        default="Identifier",
        init=False,
        repr=False,
    )
    quoting: Literal["QUOTED"] = field(default="QUOTED", init=False, repr=False)
    value: str

    @classmethod
    def of(cls, value: str, /) -> Self:
        return cls(value=value)

    @override
    def __str__(self) -> str:
        return _quote(self.value)


@dataclass(config=_PYDANTIC_CONFIG, frozen=True, kw_only=True)
class _AMdxCompoundIdentifier(ABC):
    element_type: Literal["CompoundIdentifier"] = field(
        default="CompoundIdentifier",
        init=False,
        repr=False,
    )
    identifiers: FrozenSequence[MdxIdentifier]

    @override
    def __str__(self) -> str:
        return ".".join(str(identifier) for identifier in self.identifiers)


@final
@dataclass(config=_PYDANTIC_CONFIG, frozen=True, kw_only=True)
class MdxHierarchyCompoundIdentifier(_AMdxCompoundIdentifier):
    type: Literal["hierarchy"] = field(default="hierarchy", init=False, repr=False)
    dimension_name: DimensionName
    hierarchy_name: HierarchyName

    @classmethod
    def of(cls, hierarchy_identifier: HierarchyIdentifier, /) -> Self:
        return cls(
            identifiers=[
                MdxIdentifier.of(
                    hierarchy_identifier.dimension_identifier.dimension_name
                ),
                MdxIdentifier.of(hierarchy_identifier.hierarchy_name),
            ],
            dimension_name=hierarchy_identifier.dimension_identifier.dimension_name,
            hierarchy_name=hierarchy_identifier.hierarchy_name,
        )


@final
@dataclass(config=_PYDANTIC_CONFIG, frozen=True, kw_only=True)
class MdxLevelCompoundIdentifier(_AMdxCompoundIdentifier):
    type: Literal["level"] = field(default="level", init=False, repr=False)
    dimension_name: DimensionName
    hierarchy_name: HierarchyName
    level_name: str

    @classmethod
    def of(cls, level_identifier: LevelIdentifier, /) -> Self:
        return cls(
            identifiers=[
                MdxIdentifier.of(
                    level_identifier.hierarchy_identifier.dimension_identifier.dimension_name
                ),
                MdxIdentifier.of(level_identifier.hierarchy_identifier.hierarchy_name),
                MdxIdentifier.of(level_identifier.level_name),
            ],
            dimension_name=level_identifier.hierarchy_identifier.dimension_identifier.dimension_name,
            hierarchy_name=level_identifier.hierarchy_identifier.hierarchy_name,
            level_name=level_identifier.level_name,
        )


@final
@dataclass(config=_PYDANTIC_CONFIG, frozen=True, kw_only=True)
class MdxMeasureCompoundIdentifier(_AMdxCompoundIdentifier):
    type: Literal["measure"] = field(default="measure", init=False, repr=False)
    measure_name: MeasureName

    @classmethod
    def of(cls, measure_identifier: MeasureIdentifier, /) -> Self:
        return cls(
            identifiers=[
                MdxIdentifier.of(
                    MEASURES_HIERARCHY_IDENTIFIER.dimension_identifier.dimension_name
                ),
                MdxIdentifier.of(measure_identifier.measure_name),
            ],
            measure_name=measure_identifier.measure_name,
        )


@final
@dataclass(config=_PYDANTIC_CONFIG, frozen=True, kw_only=True)
class MdxMemberCompoundIdentifier(_AMdxCompoundIdentifier):
    type: Literal["member"] = field(default="member", init=False, repr=False)
    dimension_name: DimensionName
    hierarchy_name: HierarchyName
    level_name: LevelName
    path: FrozenSequence[str]

    @classmethod
    def of(
        cls,
        *path: str,
        level_identifier: LevelIdentifier,
        hierarchy_first_level_name: LevelName,
    ) -> Self:
        return cls(
            identifiers=[
                MdxIdentifier.of(
                    level_identifier.hierarchy_identifier.dimension_identifier.dimension_name
                ),
                MdxIdentifier.of(level_identifier.hierarchy_identifier.hierarchy_name),
                MdxIdentifier.of(hierarchy_first_level_name),
                *[MdxIdentifier.of(value) for value in path],
            ],
            dimension_name=level_identifier.hierarchy_identifier.dimension_identifier.dimension_name,
            hierarchy_name=level_identifier.hierarchy_identifier.hierarchy_name,
            level_name=level_identifier.level_name,
            path=path,
        )


@final
@dataclass(config=_PYDANTIC_CONFIG, frozen=True, kw_only=True)
class MdxUndefinedCompoundIdentifier(_AMdxCompoundIdentifier):
    # Same as https://github.com/activeviam/activepivot/blob/76af874771345648567f0b53880ee6e12a00f40a/pivot/mdx/impl/src/main/java/com/activeviam/activepivot/mdx/impl/internal/statement/impl/CompoundIdentifier.java#L84.
    type: Literal["undefined"] = field(default="undefined", init=False, repr=False)

    @classmethod
    def of(
        cls,
        *identifiers: str,
    ) -> Self:
        return cls(
            identifiers=[MdxIdentifier.of(identifier) for identifier in identifiers]
        )


MdxCompoundIdentifier = Annotated[
    MdxMeasureCompoundIdentifier
    | MdxMemberCompoundIdentifier
    | MdxLevelCompoundIdentifier
    | MdxHierarchyCompoundIdentifier
    | MdxUndefinedCompoundIdentifier,
    Discriminator("type"),
]


@final
@dataclass(config=_PYDANTIC_CONFIG, frozen=True, kw_only=True)
class MdxFunction:
    element_type: Literal["Function"] = field(
        default="Function",
        init=False,
        repr=False,
    )
    arguments: FrozenSequence[MdxExpression]
    name: str
    syntax: Literal["Braces", "Function", "Infix", "Parentheses", "Property"]

    def __post_init__(self) -> None:
        if self.syntax == "Property":
            assert len(self.arguments) == 1

    @classmethod
    def braces(cls, arguments: Sequence[MdxExpression], /) -> Self:
        return cls(arguments=arguments, name=r"{}", syntax="Braces")

    @classmethod
    def function(cls, name: str, arguments: Sequence[MdxExpression], /) -> Self:
        return cls(arguments=arguments, name=name, syntax="Function")

    @classmethod
    def infix(cls, name: str, arguments: Sequence[MdxExpression], /) -> Self:
        return cls(arguments=arguments, name=name, syntax="Infix")

    @classmethod
    def parentheses(cls, arguments: Sequence[MdxExpression], /) -> Self:
        return cls(arguments=arguments, name="()", syntax="Parentheses")

    @classmethod
    def property(cls, name: str, argument: MdxExpression, /) -> Self:
        return cls(arguments=[argument], name=name, syntax="Property")

    @override
    def __str__(self) -> str:
        match self.syntax:
            case "Braces" | "Parentheses":
                opening_character, closing_character = list(self.name)
                return f"{opening_character}{', '.join(str(argument) for argument in self.arguments)}{closing_character}"
            case "Function":
                return f"{self.name}({', '.join(str(argument) for argument in self.arguments)})"
            case "Infix":
                return f" {self.name} ".join(
                    str(argument) for argument in self.arguments
                )
            case "Property":
                (argument,) = self.arguments
                return f"{argument!s}.{self.name}"


MdxExpression = Annotated[
    MdxLiteral | MdxIdentifier | MdxCompoundIdentifier | MdxFunction,
    Discriminator("element_type"),
]

ColumnsAxisName = Literal["COLUMNS"]
RowsAxisName = Literal["ROWS"]
RegularAxisName = Literal[ColumnsAxisName, RowsAxisName]
SlicerAxisName = Literal["SLICER"]
AxisName = Literal[RegularAxisName, SlicerAxisName]
AxisNameT_co = TypeVar("AxisNameT_co", bound=AxisName, covariant=True)


@final
@dataclass(config=_PYDANTIC_CONFIG, frozen=True, kw_only=True)
class MdxAxis(Generic[AxisNameT_co]):
    element_type: Literal["Axis"] = field(default="Axis", init=False, repr=False)
    expression: MdxExpression
    name: AxisNameT_co
    properties: FrozenSequence[MdxAst] = ()
    non_empty: bool = False

    def __post_init__(self) -> None:
        if self.name == "SLICER":
            assert not self.non_empty

    @override
    def __str__(self) -> str:
        return "".join(
            (
                "NON EMPTY " if self.non_empty else "",
                str(self.expression),
                *(
                    (
                        " DIMENSION PROPERTIES ",
                        ", ".join(
                            str(axis_property) for axis_property in self.properties
                        ),
                    )
                    if self.properties
                    else ()
                ),
                *(() if self.name == "SLICER" else (" ON ", self.name)),
            )
        )


MdxAxisBound: TypeAlias = MdxAxis[AxisName]


@final
@dataclass(config=_PYDANTIC_CONFIG, frozen=True, kw_only=True)
class MdxFromClause:
    element_type: Literal["From"] = field(default="From", init=False, repr=False)
    cube_name: CubeName

    @override
    def __str__(self) -> str:
        return f"FROM {_quote(self.cube_name)}"


_FromClauseField = Field(
    validation_alias=AliasChoices("from_clause", "from"),
    serialization_alias="from",
)


@dataclass(config=_PYDANTIC_CONFIG, frozen=True, kw_only=True)
class _AMdxSelect(ABC):
    axes: FrozenSequence[MdxAxis[RegularAxisName]]
    slicer_axis: MdxAxis[SlicerAxisName] | None = None
    from_clause: Annotated[
        MdxSubSelect | MdxFromClause,
        _FromClauseField,
    ]

    @override
    def __str__(self) -> str:
        return "".join(
            (
                "SELECT ",
                *(
                    (", ".join(str(axis) for axis in self.axes), " ")
                    if self.axes
                    else ()
                ),
                str(self.from_clause),
                *((f" WHERE {self.slicer_axis}",) if self.slicer_axis else ()),
            )
        )


@final
@dataclass(config=_PYDANTIC_CONFIG, frozen=True, kw_only=True)
class MdxSelect(_AMdxSelect):
    element_type: Literal["Select"] = field(default="Select", init=False, repr=False)
    # Not redefining this attribute causes Pydantic to not alias it to `from` when serializing.
    from_clause: Annotated[
        MdxSubSelect | MdxFromClause,
        _FromClauseField,
    ]
    with_clause: FrozenSequence[object] = field(default=(), init=False, repr=False)

    def __post_init__(self) -> None:
        assert not self.with_clause


@final
@dataclass(config=_PYDANTIC_CONFIG, frozen=True, kw_only=True)
class MdxSubSelect(_AMdxSelect):
    element_type: Literal["SubSelect"] = field(
        default="SubSelect",
        init=False,
        repr=False,
    )
    # Not redefining this attribute causes Pydantic to not alias it to `from` when serializing.
    from_clause: Annotated[
        MdxSubSelect | MdxFromClause,
        _FromClauseField,
    ]

    @override
    def __str__(self) -> str:
        return f"FROM ({super().__str__()})"


MdxAst = Annotated[
    MdxExpression | MdxAxisBound | MdxFromClause | MdxSelect | MdxSubSelect,
    Discriminator("element_type"),
]
