from __future__ import annotations

from ..._doc import doc
from ..._escape_literal_in_format_string import escape_literal_in_format_string
from ..._experimental import experimental
from ..._measure.calculated_measure import CalculatedMeasure, Operator
from ..._measure_convertible import VariableMeasureConvertible
from ..._measure_definition import MeasureDefinition, convert_to_measure_definition
from .._strictly_positive_number import StrictlyPositiveNumber


@doc(
    formula=escape_literal_in_format_string(
        r"\operatorname {pdf}(x)=\frac {\Gamma (\frac {\nu +1}{2})}{\sqrt {\nu \pi }\,\Gamma (\frac {\nu }{2})} \left(1+\frac {x^{2}}{\nu }\right)^{-\frac {\nu +1}{2}}"
    )
)
@experimental()
def pdf(
    point: VariableMeasureConvertible,
    /,
    *,
    degrees_of_freedom: StrictlyPositiveNumber | VariableMeasureConvertible,
) -> MeasureDefinition:
    r"""Probability density function for a Student's t distribution.

    Warning:
        {experimental_feature}

    The pdf of a Student's t-distribution is:

    .. math::

        {formula}

    where :math:`\nu` is the number of degrees of freedom and :math:`\Gamma` is the gamma function.

    Args:
        point: The point where the function is evaluated.
        degrees_of_freedom: The number of degrees of freedom.
            Must be positive.

    See Also:
        `The Student's t Wikipedia page <https://en.wikipedia.org/wiki/Student%27s_t-distribution>`__.

    """
    return CalculatedMeasure(
        Operator(
            "student_density",
            [convert_to_measure_definition(arg) for arg in [point, degrees_of_freedom]],
        ),
    )
