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
    formula=escape_literal_in_format_string(
        r"\operatorname {pdf}(x) = \frac{1}{ \sigma \sqrt{2 \pi} } e^{-\frac{1}{2} \left(\frac{x - \mu}{\sigma}\right)^{2}}"
    )
)
@experimental()
def pdf(
    point: VariableMeasureConvertible,
    /,
    *,
    mean: NumericMeasureConvertible = 0,
    standard_deviation: StrictlyPositiveNumber | VariableMeasureConvertible = 1,
) -> MeasureDefinition:
    r"""Probability density function for a normal distribution.

    Warning:
        {experimental_feature}

    The pdf is given by the formula

    .. math::

        {formula}

    Where :math:`\mu` is the mean (or expectation) of the distribution while :math:`\sigma` is its standard deviation.

    Args:
        point: The point where the function is evaluated.
        mean: The mean value of the distribution.
        standard_deviation: The standard deviation of the distribution.
            Must be positive.

    See Also:
        `General normal distribution <https://en.wikipedia.org/wiki/Normal_distribution#General_normal_distribution>`__.

    """
    return CalculatedMeasure(
        Operator(
            "normal_density",
            [
                convert_to_measure_definition(arg)
                for arg in [point, mean, standard_deviation]
            ],
        ),
    )
