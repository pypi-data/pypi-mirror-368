from __future__ import annotations

from typing import Annotated, Literal

from pydantic import Field

from .._doc import doc
from .._escape_literal_in_format_string import escape_literal_in_format_string
from .._experimental import experimental
from .._measure.irr import IrrMeasure
from .._measure_convertible import VariableMeasureConvertible
from .._measure_definition import MeasureDefinition, convert_to_measure_definition
from ..hierarchy import Hierarchy


@doc(
    formula=escape_literal_in_format_string(
        r"NPV = \sum_{i=0}^{T} CF_i (1 + r)^{\frac{-t_i}{P}} = 0"
    ),
    experimental_key='{"finance.irr"}',
)
@experimental()
def irr(
    *,
    cash_flows: VariableMeasureConvertible,
    market_value: VariableMeasureConvertible,
    date: Hierarchy,
    precision: float = 0.001,
    period: Literal["annualized", "total"] = "total",
    guess: Annotated[float, Field(gt=-1)] | None = None,
) -> MeasureDefinition:
    r"""Return the Internal Rate of Return based on the underlying cash flows and market values.

    Warning:
        {experimental_feature}

    The IRR is the rate :math:`r` that nullifies the Net Present Value:

    .. math::

        {formula}

    With:

    * :math:`T` the total number of days since the beginning
    * :math:`t_i` the number of days since the beginning for date :math:`i`
    * :math:`P` the unit period in days in which the rate is expressed
    * :math:`CF_i` the enhanced cashflow for date :math:`i`

      * CF of the first day is the opposite of the market value for this day: :math:`CF_0 = - MV_0`.
      * CF of the last day is increased by the market value for this day: :math:`CF_T = cash\_flow_T + MV_T`.
      * Otherwise CF is the input cash flow: :math:`CF_i = cash\_flow_i`.

    This equation is solved using Newton's method.

    Args:
        cash_flows: The measure representing the cash flows.
        market_value: The measure representing the market value, used to enhanced the cashflows first and last value.
            If the cash flows don't need to be enhanced then ``0`` can be used.
        date: The date hierarchy.
            It must have a single date level.
        precision: The precision of the IRR value.
        period: Unit period in which to express the rate.

            * ``annualized``: The measure evaluates to a rate as a percentage per 365-day period, i.e. :math:`P = 365`.
            * ``total``: The measure evaluates to a rate over the entire date range, i.e. :math:`P = T`.
        guess: Estimated value of the IRR, used when the default guesses do not converge to a solution.

    Example:
        .. doctest::
            :hide:

            >>> session = getfixture("default_session")

        >>> from datetime import date
        >>> df = pd.DataFrame(
        ...     columns=["Date", "Market value", "Cash flow"],
        ...     data=[
        ...         (date(2023, 1, 1), 10000, 0),
        ...         (date(2023, 7, 1), 10500, 400),
        ...         (date(2024, 1, 1), 11500, 700),
        ...         (date(2024, 12, 31), 12000, 1300),
        ...         (date(2025, 7, 1), 13000, 1100),
        ...     ],
        ... )
        >>> table = session.read_pandas(df, table_name="Cash flows")
        >>> cube = session.create_cube(table)
        >>> h, m = cube.hierarchies, cube.measures
        >>> with tt.experimental({experimental_key}):
        ...     m["Annualized IRR"] = tt.finance.irr(
        ...         cash_flows=m["Cash flow.SUM"],
        ...         market_value=m["Market value.SUM"],
        ...         date=h["Date"],
        ...         precision=1e-8,
        ...         period="annualized",
        ...     )
        ...     m["Total IRR"] = tt.finance.irr(
        ...         cash_flows=m["Cash flow.SUM"],
        ...         market_value=m["Market value.SUM"],
        ...         date=h["Date"],
        ...         precision=1e-8,
        ...         period="total",
        ...     )
        >>> m["Annualized IRR"].formatter = m["Total IRR"].formatter = "DOUBLE[0.00%]"
        >>> cube.query(m["Annualized IRR"], m["Total IRR"])
          Annualized IRR Total IRR
        0         24.04%    71.30%


    See Also:
        The IRR `Wikipedia page <https://en.wikipedia.org/wiki/Internal_rate_of_return>`__.

    """
    if len(date) > 1:
        raise ValueError("The date hierarchy must have a single date level")
    return IrrMeasure(
        _cash_flows_measure=convert_to_measure_definition(cash_flows),
        _market_value_measure=convert_to_measure_definition(market_value),
        _date_hierarchy_identifier=date._identifier,
        _precision=precision,
        _period=period,
        _guess=guess,
    )
