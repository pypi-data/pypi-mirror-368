from datetime import date, datetime
from typing import final

from pydantic.dataclasses import dataclass

from ..._pydantic import PYDANTIC_CONFIG as _PYDANTIC_CONFIG


def _serialize_value(value: int | date | datetime, /) -> str:
    match value:
        case date():
            return value.isoformat()
        case int():
            return str(value)


@dataclass(config=_PYDANTIC_CONFIG, frozen=True, kw_only=True)
@final
class EmulatedTimeTravelConfig:
    empty_table_version: int | date | datetime
    """The version of an empty table (e.g ``-1``, ``date(1970, 1, 1)``, etc.)"""

    max_valid_to: int | date | datetime | None = None
    """The ``valid_to`` for a valid row or ``None`` (e.g ``1000000000``, ``date(2099, 12, 31)``, etc.)"""

    @property
    def _emulated_time_travel_options(self) -> dict[str, str]:
        return {
            "EMPTY_TABLE_VERSION": _serialize_value(self.empty_table_version),
            **(
                {
                    "VALID_ROW_TO_COLUMN_VALUE": _serialize_value(self.max_valid_to),
                }
                if self.max_valid_to
                else {}
            ),
        }
