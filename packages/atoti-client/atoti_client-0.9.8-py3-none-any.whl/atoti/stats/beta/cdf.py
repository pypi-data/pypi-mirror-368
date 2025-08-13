from __future__ import annotations

from ..._doc import doc
from ..._escape_literal_in_format_string import escape_literal_in_format_string
from ..._experimental import experimental
from ..._measure.calculated_measure import CalculatedMeasure, Operator
from ..._measure_convertible import VariableMeasureConvertible
from ..._measure_definition import MeasureDefinition, convert_to_measure_definition
from .._numeric_measure_convertible import NumericMeasureConvertible


@doc(
    formula=escape_literal_in_format_string(
        r"\operatorname {cdf}(x) = I_x(\alpha,\beta)"
    )
)
@experimental()
def cdf(
    point: VariableMeasureConvertible,
    /,
    *,
    alpha: NumericMeasureConvertible,
    beta: NumericMeasureConvertible,
) -> MeasureDefinition:
    r"""Cumulative distribution function for a beta distribution.

    Warning:
        {experimental_feature}

    The cdf of the beta distribution with shape parameters :math:`\alpha` and :math:`\beta` is

    .. math::

        {formula}

    Where :math:`I` is the `regularized incomplete beta function <https://en.wikipedia.org/wiki/Beta_function#Incomplete_beta_function>`__.

    Args:
        point: The point where the function is evaluated.
        alpha: The alpha parameter of the distribution.
        beta: The beta parameter of the distribution.

    See Also:
        `The beta distribution Wikipedia page <https://en.wikipedia.org/wiki/Beta_distribution>`__.

    """
    return CalculatedMeasure(
        Operator(
            "beta_cumulative_probability",
            [convert_to_measure_definition(arg) for arg in [point, alpha, beta]],
        ),
    )
