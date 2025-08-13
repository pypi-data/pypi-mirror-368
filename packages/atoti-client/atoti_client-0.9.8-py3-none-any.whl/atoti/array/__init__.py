"""Atoti is designed to handle array data efficiently.

There are multiple ways to load arrays into Atoti tables.
For instance:

* With :meth:`atoti.Session.read_pandas`:

  .. doctest::
      :hide:

      >>> session = getfixture("default_session")

  >>> import numpy as np
  >>> df = pd.DataFrame(
  ...     columns=["NumPy array", "Python list"],
  ...     data=[
  ...         (np.array([1.0, 2.0, 3.0]), [1, 2, 3]),
  ...         (np.array([4.0, 5.0, 6.0]), [4, 5, 6]),
  ...         (np.array([7.0, 8.0, 9.0]), [7, 8, 9]),
  ...     ],
  ... )
  >>> pandas_table = session.read_pandas(df, table_name="DataFrame with arrays")
  >>> pandas_table.head()
         NumPy array Python list
  0  [1.0, 2.0, 3.0]   [1, 2, 3]
  1  [4.0, 5.0, 6.0]   [4, 5, 6]
  2  [7.0, 8.0, 9.0]   [7, 8, 9]

* With :meth:`atoti.Session.read_csv`:

  >>> pnl_table = session.read_csv(
  ...     TEST_RESOURCES_PATH / "csv" / "pnl.csv",
  ...     array_separator=";",
  ...     keys={"Continent", "Country"},
  ...     table_name="PnL",
  ... )
  >>> pnl_table.head().sort_index()
                                                                   PnL
  Continent Country
  America   Mexico   [-10.716, 9.593, 1.356, -21.185, 5.989, 9.686,...
  Asia      China    [-1.715, 2.425, -4.059, 4.102, -2.331, -2.662,...
            India    [-18.716, 8.583, -41.356, -11.138, 3.949, 5.66...
  Europe    France   [-0.465, -0.025, 0.601, 0.423, -0.815, 0.024, ...
            UK       [11.449, -35.5464, -66.641, -48.498, -6.3126, ...

As for scalar measures, Atoti provides the default :guilabel:`SUM` and :guilabel:`MEAN` aggregations on array measures.
They are applied element by element:

  >>> cube = session.create_cube(pnl_table)
  >>> l, m = cube.levels, cube.measures
  >>> cube.query(m["PnL.SUM"], m["PnL.MEAN"], levels=[l["Continent"]])
                                    PnL.SUM                         PnL.MEAN
  Continent
  America    doubleVector[10]{-10.716, ...}   doubleVector[10]{-10.716, ...}
  Asia       doubleVector[10]{-20.431, ...}  doubleVector[10]{-10.2155, ...}
  Europe      doubleVector[10]{10.984, ...}     doubleVector[10]{5.492, ...}

Besides the functions below, arrays support the following operations:

* Arithmetic operators:

  >>> m["PnL +10"] = m["PnL.SUM"] + 10.0
  >>> cube.query(m["PnL +10"])
                            PnL +10
  0  doubleVector[10]{-10.163, ...}

  >>> m["PnL -10"] = m["PnL.SUM"] - 10.0
  >>> cube.query(m["PnL -10"])
                            PnL -10
  0  doubleVector[10]{-30.163, ...}

  >>> m["PnL x10"] = m["PnL.SUM"] * 10.0
  >>> cube.query(m["PnL x10"])
                            PnL x10
  0  doubleVector[10]{-201.63, ...}

  >>> m["PnL /10"] = m["PnL.SUM"] / 10.0
  >>> cube.query(m["PnL /10"])
                            PnL /10
  0  doubleVector[10]{-2.0163, ...}

* Indexing:

  >>> m["First element"] = m["PnL.SUM"][0]
  >>> cube.query(m["First element"], m["PnL.SUM"])
    First element                         PnL.SUM
  0        -20.16  doubleVector[10]{-20.163, ...}

  This can be used with :meth:`atoti.Cube.create_parameter_hierarchy_from_members` to "slice" the array:

  >>> cube.create_parameter_hierarchy_from_members("Index", list(range(0, 10)))
  >>> m["PnL at index"] = m["PnL.SUM"][l["Index"]]
  >>> cube.query(m["PnL at index"], levels=[l["Index"]])
        PnL at index
  Index
  0           -20.16
  1           -14.97
  2          -110.10
  3           -76.30
  4              .48
  5           -57.51
  6             -.53
  7           -15.49
  8           -22.97
  9             9.26

  Non-integer hierarchies can also be created:

  >>> from datetime import date, timedelta
  >>> dates = [date(2020, 1, 1) + timedelta(days=offset) for offset in range(0, 10)]
  >>> cube.create_parameter_hierarchy_from_members(
  ...     "Dates", dates, index_measure_name="Date index"
  ... )
  >>> m["PnL at date"] = m["PnL.SUM"][m["Date index"]]
  >>> cube.query(m["Date index"], m["PnL at date"], levels=[l["Dates"]])
             Date index PnL at date
  Dates
  2020-01-01          0      -20.16
  2020-01-02          1      -14.97
  2020-01-03          2     -110.10
  2020-01-04          3      -76.30
  2020-01-05          4         .48
  2020-01-06          5      -57.51
  2020-01-07          6        -.53
  2020-01-08          7      -15.49
  2020-01-09          8      -22.97
  2020-01-10          9        9.26

* Slicing:

  >>> m["First 2 elements"] = m["PnL.SUM"][0:2]
  >>> cube.query(m["First 2 elements"], m["PnL.SUM"])
                  First 2 elements                         PnL.SUM
  0  doubleVector[2]{-20.163, ...}  doubleVector[10]{-20.163, ...}

* Selecting elements at given indices:

  A ``Tuple[int, ...]`` or a measure of type :data:`~atoti.type.INT_ARRAY` or :data:`~atoti.type.LONG_ARRAY` can be provided to create another array measure containing the values at the passed indices:

  >>> m["First and last"] = m["PnL.SUM"][0, -1]
  >>> cube.query(m["First and last"])
                    First and last
  0  doubleVector[2]{-20.163, ...}

"""

from .len import len as len  # noqa: A004
from .max import max as max  # noqa: A004
from .mean import mean as mean
from .min import min as min  # noqa: A004
from .n_greatest import n_greatest as n_greatest
from .n_greatest_indices import n_greatest_indices as n_greatest_indices
from .n_lowest import n_lowest as n_lowest
from .n_lowest_indices import n_lowest_indices as n_lowest_indices
from .negative_values import negative_values as negative_values
from .nth_greatest import nth_greatest as nth_greatest
from .nth_lowest import nth_lowest as nth_lowest
from .positive_values import positive_values as positive_values
from .prefix_sum import prefix_sum as prefix_sum
from .prod import prod as prod
from .quantile import quantile as quantile
from .quantile_index import quantile_index as quantile_index
from .replace import replace as replace
from .sort import sort as sort
from .std import std as std
from .sum import sum as sum  # noqa: A004
from .var import var as var
