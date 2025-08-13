from __future__ import annotations

from ...._identification import ExternalColumnIdentifier, Identifiable
from .._external_measure import ExternalMeasure


def count(
    *,
    aggregate_column: Identifiable[ExternalColumnIdentifier],
) -> ExternalMeasure:
    return ExternalMeasure(
        aggregation_key="COUNT",
        granular_columns=[],
        aggregate_columns=[aggregate_column],
    )
