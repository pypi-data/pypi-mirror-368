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
        r"\operatorname {pdf}(x)=\dfrac {x^{\frac {k}{2}-1}e^{-\frac {x}{2}}}{2^\frac {k}{2}\Gamma \left(\frac {k}{2}\right)}"
    )
)
@experimental()
def pdf(
    point: VariableMeasureConvertible,
    /,
    *,
    degrees_of_freedom: StrictlyPositiveNumber | VariableMeasureConvertible,
) -> MeasureDefinition:
    r"""Probability density function for a chi-square distribution.

    Warning:
        {experimental_feature}

    The pdf of the chi-square distribution with k degrees of freedom is

    .. math::

        {formula}

    where :math:`\Gamma` is the `gamma function <https://en.wikipedia.org/wiki/Gamma_function>`__.

    Args:
        point: The point where the function is evaluated.
        degrees_of_freedom: The number of degrees of freedom.
            Must be positive.

    See Also:
        `The Chi-square Wikipedia page <https://en.wikipedia.org/wiki/Chi-square_distribution>`__.

    """
    return CalculatedMeasure(
        Operator(
            "chi2_density",
            [convert_to_measure_definition(arg) for arg in [point, degrees_of_freedom]],
        ),
    )
