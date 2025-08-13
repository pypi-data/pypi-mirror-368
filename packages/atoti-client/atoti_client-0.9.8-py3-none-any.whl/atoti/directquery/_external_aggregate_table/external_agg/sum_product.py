from __future__ import annotations

from collections.abc import Sequence

from ...._identification import ColumnIdentifier, ExternalColumnIdentifier, Identifiable
from .._external_measure import ExternalMeasure


def sum_product(
    granular_columns: Sequence[Identifiable[ColumnIdentifier]],
    /,
    *,
    aggregate_column: Identifiable[ExternalColumnIdentifier],
) -> ExternalMeasure:
    return ExternalMeasure(
        aggregation_key="ATOTI_SUM_PRODUCT",
        granular_columns=granular_columns,
        aggregate_columns=[aggregate_column],
    )
