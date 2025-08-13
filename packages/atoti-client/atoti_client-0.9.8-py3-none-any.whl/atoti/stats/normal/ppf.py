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
    error_function_inverse=escape_literal_in_format_string(r"\operatorname {erf}^{-1}"),
    formula=escape_literal_in_format_string(
        r"\operatorname {ppf}(x) = \mu + \sigma \sqrt{2} \operatorname {erf} ^{-1}(2x-1)"
    ),
)
@experimental()
def ppf(
    point: VariableMeasureConvertible,
    /,
    *,
    mean: NumericMeasureConvertible,
    standard_deviation: StrictlyPositiveNumber | VariableMeasureConvertible,
) -> MeasureDefinition:
    r"""Percent point function for a normal distribution.

    Warning:
        {experimental_feature}

    Also called inverse cumulative distribution function.

    The ppf is given by the formula

    .. math::

       {formula}

    Where :math:`\mu` is the mean of the distribution, :math:`\sigma` is its standard deviation and :math:`{error_function_inverse}` the inverse of the error function.

    Args:
        point: The point where the function is evaluated.
        mean: The mean value of the distribution.
        standard_deviation: The standard deviation of the distribution.
            Must be positive.

    See Also:
        `Quantile function of a normal distribution <https://en.wikipedia.org/wiki/Normal_distribution#Quantile_function>`__.

    """
    return CalculatedMeasure(
        Operator(
            "normal_ppf",
            [
                convert_to_measure_definition(arg)
                for arg in [point, mean, standard_deviation]
            ],
        ),
    )
