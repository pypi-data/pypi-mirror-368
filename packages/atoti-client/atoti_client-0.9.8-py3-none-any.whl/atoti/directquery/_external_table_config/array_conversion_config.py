from abc import ABC

from pydantic.dataclasses import dataclass

from ..._pydantic import PYDANTIC_CONFIG as _PYDANTIC_CONFIG
from ..array_conversion import MultiColumnArrayConversion, MultiRowArrayConversion


@dataclass(config=_PYDANTIC_CONFIG, frozen=True, kw_only=True)
class ArrayConversionConfig(ABC):  # noqa: B024
    array_conversion: MultiColumnArrayConversion | MultiRowArrayConversion | None = None
    """Config to convert some values spread over multiple columns or rows into array columns."""
