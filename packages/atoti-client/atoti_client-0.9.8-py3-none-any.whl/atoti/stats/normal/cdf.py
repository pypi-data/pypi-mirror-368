from __future__ import annotations

from ..._doc import doc
from ..._escape_literal_in_format_string import escape_literal_in_format_string
from ..._experimental import experimental
from ..._measure.calculated_measure import CalculatedMeasure, Operator
from ..._measure_convertible import VariableMeasureConvertible
from ..._measure_definition import MeasureDefinition, convert_to_measure_definition
from .._numeric_measure_convertible import NumericMeasureConvertible
from .._strictly_positive_number import StrictlyPositiveNumber


@doc(
    erf=escape_literal_in_format_string(r"\operatorname {erf}"),
    formula=escape_literal_in_format_string(
        r"\operatorname {cdf}(x) = \frac {1}{2}\left[1 + \operatorname {erf} \left(\frac {x-\mu }{\sigma {\sqrt {2}}}\right)\right]"
    ),
)
@experimental()
def cdf(
    point: VariableMeasureConvertible,
    /,
    *,
    mean: NumericMeasureConvertible,
    standard_deviation: StrictlyPositiveNumber | VariableMeasureConvertible,
) -> MeasureDefinition:
    r"""Cumulative distribution function for a normal distribution.

    Warning:
        {experimental_feature}

    The cdf is given by the formula

    .. math::

       {formula}

    Where :math:`\mu` is the mean of the distribution, :math:`\sigma` is its standard deviation and :math:`{erf}` the error function.

    Args:
        point: The point where the function is evaluated.
        mean: The mean value of the distribution.
        standard_deviation: The standard deviation of the distribution.
            Must be positive.

    See Also:
        `cdf of a normal distribution <https://en.wikipedia.org/wiki/Normal_distribution#Cumulative_distribution_function>`__.

    """
    return CalculatedMeasure(
        Operator(
            "normal_cumulative_probability",
            [
                convert_to_measure_definition(arg)
                for arg in [point, mean, standard_deviation]
            ],
        ),
    )
