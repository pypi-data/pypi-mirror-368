from __future__ import annotations

from collections.abc import Mapping

from .._measure.generic_measure import GenericMeasure
from .._measure_convertible import VariableMeasureConvertible
from .._measure_definition import MeasureDefinition, convert_to_measure_definition
from ._utils import check_array_type


def replace(
    measure: VariableMeasureConvertible,
    replacements: Mapping[float, float] | Mapping[int, int],
    /,
) -> MeasureDefinition:
    """Return a measure where elements equal to a key of the *replacements* mapping are replaced with the corresponding value.

    Args:
        measure: The array measure in which to replace the elements.
        replacements: The mapping from the old values to the new ones.

    Example:
        .. doctest::
            :hide:

            >>> session = getfixture("default_session")

        >>> import math
        >>> df = pd.DataFrame(
        ...     columns=["Store ID", "New Price", "Old Price"],
        ...     data=[
        ...         ("Store 1", [12, 6, 2, 20], [6, 3, 0, 10]),
        ...         ("Store 2", [16, 8, 12, 15], [4, 4, 6, 3]),
        ...         ("Store 3", [8, -10, 0, 33], [8, 0, 2, 11]),
        ...     ],
        ... )
        >>> table = session.read_pandas(df, keys={"Store ID"}, table_name="Prices")
        >>> cube = session.create_cube(table)
        >>> l, m = cube.levels, cube.measures
        >>> m["Price ratio"] = m["New Price.SUM"] / m["Old Price.SUM"]
        >>> m["Price ratio without infinity"] = tt.array.replace(
        ...     m["Price ratio"], {math.inf: 1, -math.inf: -1}
        ... )
        >>> m["Price ratio"].formatter = "ARRAY[',']"
        >>> m["Price ratio without infinity"].formatter = "ARRAY[',']"
        >>> cube.query(
        ...     m["Price ratio"],
        ...     m["Price ratio without infinity"],
        ...     levels=[l["Store ID"]],
        ... )
                            Price ratio Price ratio without infinity
        Store ID
        Store 1    2.0,2.0,Infinity,2.0              2.0,2.0,1.0,2.0
        Store 2         4.0,2.0,2.0,5.0              4.0,2.0,2.0,5.0
        Store 3   1.0,-Infinity,0.0,3.0             1.0,-1.0,0.0,3.0

    """
    check_array_type(measure)
    return GenericMeasure(
        "VECTOR_REPLACE",
        replacements,
        [convert_to_measure_definition(measure)],
    )
