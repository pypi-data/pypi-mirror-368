from __future__ import annotations

from ..._doc import doc
from ..._escape_literal_in_format_string import escape_literal_in_format_string
from ..._experimental import experimental
from ..._measure.calculated_measure import CalculatedMeasure, Operator
from ..._measure_convertible import VariableMeasureConvertible
from ..._measure_definition import MeasureDefinition, convert_to_measure_definition
from .._strictly_positive_number import StrictlyPositiveNumber


@doc(
    beta=escape_literal_in_format_string(r"\mathrm {B}"),
    formula=escape_literal_in_format_string(
        r"\operatorname {pdf}(x) = \frac {\sqrt {\frac {(d_{1}x)^{d_{1}}\,\,d_{2}^{d_{2}}}{(d_{1}x+d_{2})^{d_{1}+d_{2}}}}} {x\,\mathrm {B} \!\left(\frac {d_{1}}{2},\frac {d_{2}}{2}\right)}"
    ),
)
@experimental()
def pdf(
    point: VariableMeasureConvertible,
    /,
    *,
    numerator_degrees_of_freedom: StrictlyPositiveNumber | VariableMeasureConvertible,
    denominator_degrees_of_freedom: StrictlyPositiveNumber | VariableMeasureConvertible,
) -> MeasureDefinition:
    r"""Probability density function for a F-distribution.

    Warning:
        {experimental_feature}

    The pdf for a F-distributions with parameters :math:`d1` et :math:`d2` is

    .. math::

        {formula}

    Where :math:`{beta}` is the beta function.

    Args:
        point: The point where the function is evaluated.
        numerator_degrees_of_freedom: Numerator degrees of freedom.
            Must be positive.
        denominator_degrees_of_freedom: Denominator degrees of freedom.
            Must be positive.

    See Also:
        `The F-distribution Wikipedia page <https://en.wikipedia.org/wiki/F-distribution>`__.

    """
    return CalculatedMeasure(
        Operator(
            "F_density",
            [
                convert_to_measure_definition(arg)
                for arg in [
                    point,
                    numerator_degrees_of_freedom,
                    denominator_degrees_of_freedom,
                ]
            ],
        ),
    )
