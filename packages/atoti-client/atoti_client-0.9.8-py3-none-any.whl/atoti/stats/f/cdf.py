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
        r"\operatorname {cdf}(x) = I_{\frac {d_{1}x}{d_{1}x+d_{2}}} \left(\tfrac {d_{1}}{2},\tfrac {d_{2}}{2}\right)"
    )
)
@experimental()
def cdf(
    point: VariableMeasureConvertible,
    /,
    *,
    numerator_degrees_of_freedom: StrictlyPositiveNumber | VariableMeasureConvertible,
    denominator_degrees_of_freedom: StrictlyPositiveNumber | VariableMeasureConvertible,
) -> MeasureDefinition:
    r"""Cumulative distribution function for a F-distribution.

    Warning:
        {experimental_feature}

    The cdf for a F-distributions with parameters :math:`d1` et :math:`d2` is

    .. math::

        {formula}

    where I is the `regularized incomplete beta function <https://en.wikipedia.org/wiki/Beta_function#Incomplete_beta_function>`__.

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
            "F_cumulative_probability",
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
