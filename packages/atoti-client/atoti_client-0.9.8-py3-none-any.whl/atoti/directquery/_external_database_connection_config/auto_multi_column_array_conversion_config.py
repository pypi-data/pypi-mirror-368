from abc import ABC

from pydantic.dataclasses import dataclass

from ..._pydantic import PYDANTIC_CONFIG as _PYDANTIC_CONFIG
from ..array_conversion import AutoMultiColumnArrayConversion


@dataclass(config=_PYDANTIC_CONFIG, frozen=True, kw_only=True)
class AutoMultiColumnArrayConversionConfig(ABC):  # noqa: B024
    auto_multi_column_array_conversion: AutoMultiColumnArrayConversion | None = None
    """When not ``None``, multi-column array conversion will be performed automatically."""

    @property
    def _auto_multi_array_conversion_options(self) -> dict[str, str]:
        return (
            {
                "USE_AUTO_VECTORIZER": str(True),
                "AUTO_VECTORIZER_DELIMITER": self.auto_multi_column_array_conversion.separator,
                "MIN_THRESHOLD_FOR_AUTO_VECTORIZER": str(
                    self.auto_multi_column_array_conversion.threshold,
                ),
            }
            if self.auto_multi_column_array_conversion
            else {}
        )
