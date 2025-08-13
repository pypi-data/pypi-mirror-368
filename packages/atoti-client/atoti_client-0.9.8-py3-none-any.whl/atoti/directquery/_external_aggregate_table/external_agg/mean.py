from __future__ import annotations

from ...._identification import ColumnIdentifier, ExternalColumnIdentifier, Identifiable
from .._external_measure import ExternalMeasure


def mean(
    granular_column: Identifiable[ColumnIdentifier],
    /,
    *,
    sum_aggregate_column: Identifiable[ExternalColumnIdentifier],
    count_aggregate_column: Identifiable[ExternalColumnIdentifier],
) -> ExternalMeasure:
    return ExternalMeasure(
        aggregation_key="AVG",
        granular_columns=[granular_column],
        aggregate_columns=[sum_aggregate_column, count_aggregate_column],
    )
