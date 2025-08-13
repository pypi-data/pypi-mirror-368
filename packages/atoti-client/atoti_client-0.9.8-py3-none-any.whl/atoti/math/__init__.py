"""On top of the functions listed below, measures can also be combined with mathematical operators.

.. doctest::
    :hide:

    >>> session = getfixture("default_session")

* The classic ``+``, ``-`` and ``*`` operators:

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
    >>> m["Sum"] = m["A.SUM"] + m["B.SUM"]
    >>> m["Subtract"] = m["A.SUM"] - m["B.SUM"]
    >>> m["Multiply"] = m["A.SUM"] * m["B.SUM"]
    >>> cube.query(
    ...     m["A.SUM"],
    ...     m["B.SUM"],
    ...     m["Sum"],
    ...     m["Subtract"],
    ...     m["Multiply"],
    ...     levels=[l["City"]],
    ... )
               A.SUM  B.SUM     Sum Subtract Multiply
    City
    Berlin     15.00  10.00   25.00     5.00   150.00
    London     24.00  16.00   40.00     8.00   384.00
    New York  -27.00  15.00  -12.00   -42.00  -405.00
    Paris        .00    .00     .00      .00      .00

* The float division ``/`` and integer division ``//``:

    >>> m["Float division"] = m["A.SUM"] / m["B.SUM"]
    >>> m["Int division"] = m["A.SUM"] // m["B.SUM"]
    >>> cube.query(
    ...     m["A.SUM"],
    ...     m["B.SUM"],
    ...     m["Float division"],
    ...     m["Int division"],
    ...     levels=[l["City"]],
    ... )
               A.SUM  B.SUM Float division Int division
    City
    Berlin     15.00  10.00           1.50         1.00
    London     24.00  16.00           1.50         1.00
    New York  -27.00  15.00          -1.80        -2.00
    Paris        .00    .00            NaN          NaN

* The exponentiation ``**``:

    >>> m["a²"] = m["A.SUM"] ** 2
    >>> cube.query(m["A.SUM"], m["a²"], levels=[l["City"]])
               A.SUM      a²
    City
    Berlin     15.00  225.00
    London     24.00  576.00
    New York  -27.00  729.00
    Paris        .00     .00

* The modulo ``%``:

    >>> m["Modulo"] = m["A.SUM"] % m["B.SUM"]
    >>> cube.query(m["A.SUM"], m["B.SUM"], m["Modulo"], levels=[l["City"]])
               A.SUM  B.SUM Modulo
    City
    Berlin     15.00  10.00   5.00
    London     24.00  16.00   8.00
    New York  -27.00  15.00   3.00
    Paris        .00    .00    NaN

"""

from .abs import abs as abs  # noqa: A004
from .ceil import ceil as ceil
from .cos import cos as cos
from .erf import erf as erf
from .erfc import erfc as erfc
from .exp import exp as exp
from .floor import floor as floor
from .isnan import isnan as isnan
from .log import log as log
from .log10 import log10 as log10
from .max import max as max  # noqa: A004
from .min import min as min  # noqa: A004
from .round import round as round  # noqa: A004
from .sin import sin as sin
from .sqrt import sqrt as sqrt
from .tan import tan as tan
