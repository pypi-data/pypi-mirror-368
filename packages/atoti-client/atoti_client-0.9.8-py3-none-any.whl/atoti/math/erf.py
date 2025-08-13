from __future__ import annotations

from .._measure.calculated_measure import CalculatedMeasure, Operator
from .._measure_convertible import VariableMeasureConvertible
from .._measure_definition import MeasureDefinition, convert_to_measure_definition


def erf(measure: VariableMeasureConvertible, /) -> MeasureDefinition:
    """Return the error function of the input measure.

    This can be used to compute traditional statistical measures such as the cumulative standard normal distribution.

    For more information read:

    * Python's built-in :func:`math.erf`
    * `scipy.special.erf <https://docs.scipy.org/doc/scipy/reference/generated/scipy.special.erf.html>`__
    * `The Wikipedia page <https://en.wikipedia.org/wiki/Error_function#Numerical_approximations>`__

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
        >>> m["erf"] = tt.math.erf(m["D.SUM"])
        >>> m["erf"].formatter = "DOUBLE[#,##0.000000]"
        >>> cube.query(m["D.SUM"], m["erf"], levels=[l["City"]])
                  D.SUM       erf
        City
        Berlin     1.00  0.842701
        London     3.14  0.999991
        New York  10.00  1.000000
        Paris       .00  0.000000

    """
    return CalculatedMeasure(Operator("erf", [convert_to_measure_definition(measure)]))
