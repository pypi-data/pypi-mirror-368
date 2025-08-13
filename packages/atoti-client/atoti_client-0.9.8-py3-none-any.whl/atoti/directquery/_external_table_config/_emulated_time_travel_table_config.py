from typing import final

from pydantic.dataclasses import dataclass

from ..._pydantic import PYDANTIC_CONFIG as _PYDANTIC_CONFIG


@dataclass(config=_PYDANTIC_CONFIG, frozen=True, kw_only=True)
@final
class EmulatedTimeTravelTableConfig:
    valid_from_column_name: str
    """The name in the external table of the :guilabel:`valid_from` column."""

    valid_to_column_name: str | None = None
    """The name in the external table of the :guilabel:`valid_to` column, if it exists."""
