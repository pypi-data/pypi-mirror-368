from __future__ import annotations

from typing import Literal, TypeAlias, overload
from warnings import warn

from typing_extensions import deprecated

from .._data_type import is_temporal_type
from .._deprecated_warning_category import (
    DEPRECATED_WARNING_CATEGORY as _DEPRECATED_WARNING_CATEGORY,
)
from .._measure.date_shift import DateShift
from .._measure_convertible import VariableMeasureConvertible
from .._measure_definition import MeasureDefinition, convert_to_measure_definition
from ..hierarchy import Hierarchy

_DateShiftFallback: TypeAlias = Literal["past", "interpolated", "future"]
_DateShiftMethod: TypeAlias = Literal[
    "exact", "previous", "next", "interpolate", "dense"
]


@overload
def date_shift(
    measure: VariableMeasureConvertible,
    on: Hierarchy,
    /,
    *,
    offset: str,
    dense: bool = False,
    fallback: _DateShiftFallback | None = None,
) -> MeasureDefinition: ...


@overload
@deprecated("The `method` parameter is deprecated, use `fallback` instead.")
def date_shift(
    measure: VariableMeasureConvertible,
    on: Hierarchy,
    /,
    *,
    offset: str,
    method: _DateShiftMethod = "exact",
) -> MeasureDefinition: ...


def date_shift(
    measure: VariableMeasureConvertible,
    on: Hierarchy,
    /,
    *,
    offset: str,
    dense: bool = False,
    fallback: _DateShiftFallback | None = None,
    method: _DateShiftMethod | None = None,
) -> MeasureDefinition:
    """Return a measure equal to the passed measure shifted to another date.

    Args:
        measure: The measure to shift.
        on: The hierarchy to shift on.
            Only hierarchies with their last level with a :attr:`~atoti.Level.data_type` of ``"LocalDate"`` or ``"LocalDateTime"`` are supported.
        offset: The period to shift by as specified by `Java's Period.parse() <https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/time/Period.html#parse(java.lang.CharSequence)>`__.
        dense: If ``False``, the returned measure will evaluate to ``None`` everywhere the input *measure* evaluates to ``None``.

            If ``True``, the returned measure will be evaluated on all the queried members of the *on* hierarchy, even if the input *measure* evaluates to ``None`` there.

            In any case, facts are never "created": if *measure* evaluates to a non-``None`` value on :guilabel:`2025-01-01` and ``offset="-P2D"`` but :guilabel:`2025-01-03` is not a member of the *on* hierarchy, :guilabel:`2025-01-03` will remain absent from the query results.
        fallback: The value to use if *measure* evaluates to ``None`` at the shifted location:

            * ``None``: No value.
            * ``past``: Value at the previous date in chronological order.
            * ``interpolated``: Linear interpolation of the values at the past and future existing dates or ``None`` if either date is missing.
            * ``future``: Value at the next date in chronological order.

    Example:
        .. doctest::
            :hide:

            >>> session = getfixture("default_session")

        >>> from datetime import date
        >>> df = pd.DataFrame(
        ...     columns=["Date", "Price"],
        ...     data=[
        ...         (date(2020, 8, 1), 5),
        ...         (date(2020, 8, 15), 7),
        ...         (date(2020, 8, 30), 15),
        ...         (date(2020, 8, 31), 15),
        ...         (date(2020, 9, 1), 10),
        ...         (date(2020, 9, 30), 21),
        ...         (date(2020, 10, 1), 9),
        ...         (date(2020, 10, 31), 8),
        ...     ],
        ... )
        >>> table = session.read_pandas(
        ...     df, keys={"Date"}, table_name="Fallback example"
        ... )
        >>> cube = session.create_cube(table)
        >>> h, l, m = cube.hierarchies, cube.levels, cube.measures
        >>> cube.create_date_hierarchy(
        ...     "Date parts",
        ...     column=table["Date"],
        ...     levels={"Year": "y", "Month": "M"},
        ... )
        >>> h["Date"] = {**h["Date parts"], "Date": table["Date"]}
        >>> m["Exact (+)"] = tt.date_shift(m["Price.SUM"], h["Date"], offset="P1M")
        >>> m["Exact (-)"] = tt.date_shift(m["Price.SUM"], h["Date"], offset="-P1M")
        >>> m["Past"] = tt.date_shift(
        ...     m["Price.SUM"], h["Date"], offset="P1M", fallback="past"
        ... )
        >>> m["Interpolated"] = tt.date_shift(
        ...     m["Price.SUM"], h["Date"], offset="P1M", fallback="interpolated"
        ... )
        >>> m["Future"] = tt.date_shift(
        ...     m["Price.SUM"], h["Date"], offset="P1M", fallback="future"
        ... )
        >>> cube.query(
        ...     m["Price.SUM"],
        ...     m["Exact (+)"],
        ...     m["Exact (-)"],
        ...     m["Past"],
        ...     m["Interpolated"],
        ...     m["Future"],
        ...     levels=[l["Date"]],
        ...     include_totals=True,
        ... )
                               Price.SUM Exact (+) Exact (-) Past Interpolated Future
        Year  Month Date
        Total                         90
        2020                          90
              8                       42
                    2020-08-01         5        10             10        10.00     10
                    2020-08-15         7                       10        15.31     21
                    2020-08-30        15        21             21        21.00     21
                    2020-08-31        15        21             21        21.00     21
              9                       31
                    2020-09-01        10         9         5    9         9.00      9
                    2020-09-30        21                  15    9         8.03      8
              10                      17
                    2020-10-01         9                  10    8
                    2020-10-31         8                  21    8

        Explanations:

        * :guilabel:`"Exact (+)`:

          * The value for :guilabel:`2020-08-31` is taken from :guilabel:`2020-09-30` even though ``31 != 30`` because there are both the last day of their respective month.

        * :guilabel:`"Exact (-)`:

          * The value for :guilabel:`2020-10-31` is taken from :guilabel:`2020-09-30` for the same reason.

        * :guilabel:`Interpolated`:

          * :guilabel:`10.00`, :guilabel:`21.00`, :guilabel:`21.00`, and :guilabel:`9.00`: no interpolation required since there is an exact match.
          * :guilabel:`15.31`: linear interpolation of :guilabel:`2020-09-01`'s :guilabel:`10` and :guilabel:`2020-09-30`'s :guilabel:`21` at :guilabel:`2020-09-15`.
          * :guilabel:`8.03`: linear interpolation of :guilabel:`2020-10-01`'s :guilabel:`9` and :guilabel:`2020-10-31`'s :guilabel:`8` at :guilabel:`2020-10-30`.
          * ∅: no interpolation possible because there are no records after ``2020-10-31``.

        Behavior of the *dense* parameter:

        >>> df = pd.DataFrame(
        ...     columns=["Date", "City", "Price"],
        ...     data=[
        ...         (date(2020, 8, 1), "London", 10),
        ...         (date(2020, 8, 1), "New York", 12),
        ...         (date(2020, 9, 1), "New York", 15),
        ...         (date(2020, 10, 1), "London", 18),
        ...         (date(2020, 10, 1), "New York", 20),
        ...     ],
        ... )
        >>> table = session.read_pandas(
        ...     df, keys={"Date", "City"}, table_name="Dense example"
        ... )
        >>> cube = session.create_cube(table)
        >>> h, l, m = cube.hierarchies, cube.levels, cube.measures
        >>> cube.create_date_hierarchy(
        ...     "Date parts", column=table["Date"], levels={"Year": "y", "Month": "M"}
        ... )
        >>> h["Date"] = {**h["Date parts"], "Date": table["Date"]}
        >>> m["Sparse"] = tt.date_shift(
        ...     m["Price.SUM"], h["Date"], offset="P1M", dense=False
        ... )
        >>> m["Dense"] = tt.date_shift(
        ...     m["Price.SUM"], h["Date"], offset="P1M", dense=True
        ... )
        >>> cube.query(
        ...     m["Price.SUM"], m["Sparse"], m["Dense"], levels=[l["Date"], l["City"]]
        ... )
                                       Price.SUM Sparse Dense
        Year Month Date       City
        2020 8     2020-08-01 London          10
                              New York        12     15    15
             9     2020-09-01 London                       18
                              New York        15     20    20
             10    2020-10-01 London          18
                              New York        20

        Explanations:

        * :guilabel:`Sparse`:

          * There is no value for :guilabel:`(2020-09-01, London)` because, although both members exist separately, no fact contains both simultaneously.

        * :guilabel:`Dense`:

          * The value for :guilabel:`(2020-09-01, London)` is taken from :guilabel:`(2020-10-01, London)`.
          * There are no values for :guilabel:`2020-10-01` because :guilabel:`2020-11-01` is not a member of the :guilabel:`Date` hierarchy.

    """
    if not is_temporal_type(list(on.values())[-1].data_type):
        raise ValueError(
            f"The hierarchy {on.name} should have a temporal deepest level.",
        )

    if method is not None:
        warn(
            "The `method` parameter is deprecated, use `fallback` instead.",
            category=_DEPRECATED_WARNING_CATEGORY,
            stacklevel=2,
        )
    else:
        method = _get_method_for_dense_and_fallback_values(
            dense=dense, fallback=fallback
        )

    return DateShift(
        _underlying_measure=convert_to_measure_definition(measure),
        _level_identifier=list(on.values())[-1]._identifier,
        _shift=offset,
        _method=method,
    )


def _get_method_for_dense_and_fallback_values(
    *, dense: bool, fallback: _DateShiftFallback | None
) -> _DateShiftMethod:
    match dense, fallback:
        case False, None:
            return "exact"
        case False, "past":
            return "previous"
        case False, "interpolated":
            return "interpolate"
        case False, "future":
            return "next"
        case True, None:
            return "dense"
        case _:
            raise ValueError(
                f"Fallback `{fallback}` is not supported when `dense={dense}`."
            )
