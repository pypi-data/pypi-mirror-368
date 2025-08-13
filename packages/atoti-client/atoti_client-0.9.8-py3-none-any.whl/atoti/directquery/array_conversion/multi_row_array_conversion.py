from collections.abc import Set as AbstractSet
from typing import final

from pydantic.dataclasses import dataclass

from ..._pydantic import PYDANTIC_CONFIG as _PYDANTIC_CONFIG


@final
@dataclass(config=_PYDANTIC_CONFIG, frozen=True, kw_only=True)
class MultiRowArrayConversion:
    """Convert an external table where array values are stored with one value per row to a table with array columns.

    The external table must have an :attr:`index_column` and at least one "value" column representing the array elements.

    All the table columns except from :attr:`index_column` and the :attr:`array_columns` will become key columns.

    Example:
        .. doctest::
            :hide:

            >>> import os
            >>> from atoti_directquery_snowflake import ConnectionConfig, TableConfig
            >>> connection_config = ConnectionConfig(
            ...     url="jdbc:snowflake://"
            ...     + os.environ["SNOWFLAKE_ACCOUNT_IDENTIFIER"]
            ...     + ".snowflakecomputing.com/?user="
            ...     + os.environ["SNOWFLAKE_USERNAME"]
            ...     + "&database=TEST_RESOURCES"
            ...     + "&schema=TESTS",
            ...     password=os.environ["SNOWFLAKE_PASSWORD"],
            ... )
            >>> session = getfixture("session_with_directquery_snowflake_plugin")

        >>> external_database = session.connect_to_external_database(connection_config)
        >>> external_table = external_database.tables["TUTORIAL", "MULTI_ROW_QUANTITY"]

        ``external_table`` has an :guilabel:`INDEX` column:

        >>> list(external_table)
        ['PRODUCT', 'INDEX', 'QUANTITY']

        and its content is:

        +-----------+-------+----------+
        | PRODUCT   | INDEX | QUANTITY |
        +===========+=======+==========+
        | product_1 |     0 |     10.0 |
        +-----------+-------+----------+
        | product_1 |     1 |     20.0 |
        +-----------+-------+----------+
        | product_1 |     2 |     15.0 |
        +-----------+-------+----------+
        | product_1 |     3 |     25.0 |
        +-----------+-------+----------+
        | product_1 |     4 |     10.0 |
        +-----------+-------+----------+
        | product_2 |     0 |     50.0 |
        +-----------+-------+----------+
        | product_2 |     1 |     65.0 |
        +-----------+-------+----------+
        | product_2 |     2 |     55.0 |
        +-----------+-------+----------+
        | product_2 |     3 |     30.0 |
        +-----------+-------+----------+
        | product_2 |     4 |     80.0 |
        +-----------+-------+----------+

        It can be converted into a table with an array column:

        >>> table = session.add_external_table(
        ...     external_table,
        ...     config=TableConfig(
        ...         array_conversion=tt.MultiRowArrayConversion(
        ...             array_columns={"QUANTITY"},
        ...             index_column="INDEX",
        ...         ),
        ...     ),
        ...     table_name="Sales (Multi row array)",
        ... )
        >>> table.head().sort_index()
                                         QUANTITY
        PRODUCT
        product_1  [10.0, 20.0, 15.0, 25.0, 10.0]
        product_2  [50.0, 65.0, 55.0, 30.0, 80.0]

    """

    index_column: str
    """Name of the column used as an index for the arrays."""

    array_columns: AbstractSet[str]
    """Names of the columns that contain array values."""
