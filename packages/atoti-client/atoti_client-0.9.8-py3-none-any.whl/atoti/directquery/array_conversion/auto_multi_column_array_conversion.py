from typing import Annotated, final

from pydantic import Field
from pydantic.dataclasses import dataclass

from ..._pydantic import PYDANTIC_CONFIG as _PYDANTIC_CONFIG


@final
@dataclass(config=_PYDANTIC_CONFIG, frozen=True, kw_only=True)
class AutoMultiColumnArrayConversion:
    """Pass it to a DirectQuery ``*ConnectionConfig`` class to automatically convert all external tables with array values stored with one element per column to tables with array columns.

    Example:
        .. doctest::
            :hide:

            >>> session = getfixture("session_with_directquery_snowflake_plugin")

        >>> import os
        >>> from atoti_directquery_snowflake import ConnectionConfig, TableConfig
        >>> url = f"jdbc:snowflake://{os.environ['SNOWFLAKE_ACCOUNT_IDENTIFIER']}.snowflakecomputing.com/?user={os.environ['SNOWFLAKE_USERNAME']}&database=TEST_RESOURCES&schema=TESTS"
        >>> connection_config = ConnectionConfig(
        ...     url=url,
        ...     auto_multi_column_array_conversion=tt.AutoMultiColumnArrayConversion(
        ...         separator="_",
        ...         threshold=3,
        ...     ),
        ...     password=os.environ["SNOWFLAKE_PASSWORD"],
        ... )
        >>> external_database = session.connect_to_external_database(connection_config)
        >>> external_table = external_database.tables[
        ...     "TUTORIAL", "MULTI_COLUMN_QUANTITY"
        ... ]

        In the external database, ``external_table`` has this content:

        +-----------+------------+------------+------------+------------+------------+
        |  PRODUCT  | QUANTITY_0 | QUANTITY_1 | QUANTITY_2 | QUANTITY_3 | QUANTITY_4 |
        +===========+============+============+============+============+============+
        | product_1 |       10.0 |       20.0 |       15.0 |       25.0 |       10.0 |
        +-----------+------------+------------+------------+------------+------------+
        | product_2 |       50.0 |       65.0 |       55.0 |       30.0 |       80.0 |
        +-----------+------------+------------+------------+------------+------------+

        It has 5 :guilabel:`QUANTITY{separator}{index}` columns (where :attr:`separator` is ``"_"``).
        Since 5 is greater than the :attr:`threshold` passed above, the automatic conversion will activate and these 5 columns will be merged into an array column:

        >>> list(external_table)
        ['PRODUCT', 'QUANTITY']
        >>> table = session.add_external_table(
        ...     external_table,
        ...     config=TableConfig(keys={"PRODUCT"}),
        ...     table_name="Sales (Multi column array)",
        ... )
        >>> table.head().sort_index()
                                         QUANTITY
        PRODUCT
        product_1  [10.0, 20.0, 15.0, 25.0, 10.0]
        product_2  [50.0, 65.0, 55.0, 30.0, 80.0]

    See Also:
        :class:`~atoti.MultiColumnArrayConversion`.
    """

    separator: str = ""
    """The characters separating the array column name and the element index."""

    threshold: Annotated[int, Field(gt=0)] = 50
    """The minimum number of columns with the same prefix required to trigger the automatic conversion."""
