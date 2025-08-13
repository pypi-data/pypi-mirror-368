from __future__ import annotations

from collections.abc import Sequence

from ...._identification import ColumnIdentifier, ExternalColumnIdentifier, Identifiable
from .._external_measure import ExternalMeasure


def agg(
    *,
    key: str,
    granular_columns: Sequence[Identifiable[ColumnIdentifier]],
    aggregate_columns: Sequence[Identifiable[ExternalColumnIdentifier]],
) -> ExternalMeasure:
    return ExternalMeasure(
        aggregation_key=key,
        granular_columns=granular_columns,
        aggregate_columns=aggregate_columns,
    )
