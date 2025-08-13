from __future__ import annotations

from ..._doc import doc
from ..._experimental import experimental
from ..._measure.calculated_measure import CalculatedMeasure, Operator
from ..._measure_convertible import VariableMeasureConvertible
from ..._measure_definition import MeasureDefinition, convert_to_measure_definition
from .._numeric_measure_convertible import NumericMeasureConvertible


@doc()
@experimental()
def ppf(
    point: VariableMeasureConvertible,
    /,
    *,
    alpha: NumericMeasureConvertible,
    beta: NumericMeasureConvertible,
) -> MeasureDefinition:
    """Percent point function for a beta distribution.

    Warning:
        {experimental_feature}

    Also called inverse cumulative distribution function.

    Args:
        point: The point where the density function is evaluated.
        alpha: The alpha parameter of the distribution.
        beta: The beta parameter of the distribution.

    See Also:
        `The beta distribution Wikipedia page <https://en.wikipedia.org/wiki/Beta_distribution>`__.

    """
    return CalculatedMeasure(
        Operator(
            "beta_ppf",
            [convert_to_measure_definition(arg) for arg in [point, alpha, beta]],
        ),
    )
