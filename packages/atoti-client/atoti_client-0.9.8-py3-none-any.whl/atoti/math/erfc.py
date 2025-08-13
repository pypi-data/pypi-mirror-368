from __future__ import annotations

from .._measure.calculated_measure import CalculatedMeasure, Operator
from .._measure_convertible import VariableMeasureConvertible
from .._measure_definition import MeasureDefinition, convert_to_measure_definition


def erfc(measure: VariableMeasureConvertible, /) -> MeasureDefinition:
    """Return the complementary error function of the input measure.

    This is the complementary of :func:`atoti.math.erf`.
    It is defined as ``1.0 - erf``.
    It can be used for large values of x where a subtraction from one would cause a loss of significance.

    Example:
        .. doctest::
            :hide:

            >>> session = getfixture("default_session")

        >>> df = pd.DataFrame(
        ...     columns=["City", "A", "B", "C", "D"],
        ...     data=[
        ...         ("Berlin", 15.0, 10.0, 10.1, 1.0),
        ...         ("London", 24.0, 16.0, 20.5, 3.14),
        ...         ("New York", -27.0, 15.0, 30.7, 10.0),
        ...         ("Paris", 0.0, 0.0, 0.0, 0.0),
        ...     ],
        ... )
        >>> table = session.read_pandas(df, keys={"City"}, table_name="Math")
        >>> cube = session.create_cube(table)
        >>> l, m = cube.levels, cube.measures
        >>> m["erfc"] = tt.math.erfc(m["D.SUM"])
        >>> m["1-erf"] = 1 - tt.math.erf(m["D.SUM"])
        >>> m["erfc"].formatter = "DOUBLE[#.00E]"
        >>> m["1-erf"].formatter = "DOUBLE[#.00E]"
        >>> cube.query(m["D.SUM"], m["erfc"], m["1-erf"], levels=[l["City"]])
                  D.SUM                    erfc                1-erf
        City
        Berlin     1.00     0.15729920705028488  0.15729920705028488
        London     3.14    8.969565553264981E-6   8.9695655532962E-6
        New York  10.00  2.0884875837625685E-45                  0.0
        Paris       .00                     1.0                  1.0

    """
    return CalculatedMeasure(
        Operator("erfc", [convert_to_measure_definition(measure)]),
    )
