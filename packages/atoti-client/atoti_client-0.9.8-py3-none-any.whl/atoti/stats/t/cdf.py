from __future__ import annotations

from ..._doc import doc
from ..._experimental import experimental
from ..._measure.calculated_measure import CalculatedMeasure, Operator
from ..._measure_convertible import VariableMeasureConvertible
from ..._measure_definition import MeasureDefinition, convert_to_measure_definition
from .._strictly_positive_number import StrictlyPositiveNumber


@doc()
@experimental()
def cdf(
    point: VariableMeasureConvertible,
    /,
    *,
    degrees_of_freedom: StrictlyPositiveNumber | VariableMeasureConvertible,
) -> MeasureDefinition:
    """Cumulative distribution function for a Student's t distribution.

    Warning:
        {experimental_feature}

    Args:
        point: The point where the function is evaluated.
        degrees_of_freedom: The number of degrees of freedom.
            Must be positive.

    See Also:
        `The Student's t Wikipedia page <https://en.wikipedia.org/wiki/Student%27s_t-distribution>`__.

    """
    return CalculatedMeasure(
        Operator(
            "student_cumulative_probability",
            [convert_to_measure_definition(arg) for arg in [point, degrees_of_freedom]],
        ),
    )
