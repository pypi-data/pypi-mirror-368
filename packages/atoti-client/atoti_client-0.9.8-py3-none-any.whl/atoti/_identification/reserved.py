from collections.abc import Set as AbstractSet

from .dimension_name import DimensionName
from .measures_hierarchy_identifier import MEASURES_HIERARCHY_IDENTIFIER

RESERVED_DIMENSION_NAMES = frozenset(
    {MEASURES_HIERARCHY_IDENTIFIER.dimension_identifier.dimension_name}
)


def _check_not_reserved(value: str, reserved: AbstractSet[str], /) -> None:
    if value in reserved:
        raise ValueError(f"`{value}` is a reserved name.")


def check_not_reserved_dimension_name(name: DimensionName, /) -> None:
    _check_not_reserved(name, RESERVED_DIMENSION_NAMES)
