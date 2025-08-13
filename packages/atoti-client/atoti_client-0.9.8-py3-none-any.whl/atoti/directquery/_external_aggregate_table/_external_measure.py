from typing import final

from pydantic.dataclasses import dataclass

from ..._collections import FrozenSequence
from ..._identification import ColumnIdentifier, ExternalColumnIdentifier, Identifiable
from ..._pydantic import PYDANTIC_CONFIG as _PYDANTIC_CONFIG


@final
@dataclass(config=_PYDANTIC_CONFIG, frozen=True, kw_only=True)
class ExternalMeasure:
    """Links the aggregated columns to their result."""

    aggregation_key: str
    granular_columns: FrozenSequence[Identifiable[ColumnIdentifier]]
    aggregate_columns: FrozenSequence[Identifiable[ExternalColumnIdentifier]]
