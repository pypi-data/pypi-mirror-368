from __future__ import annotations

from typing import Final, Literal, final, overload

from typing_extensions import override

from ._client import Client
from ._constant import Constant
from ._cube_discovery import Measure as DiscoveryMeasure, get_discovery
from ._data_type import DataType
from ._identification import CubeIdentifier, MeasureIdentifier, MeasureName
from ._operation import (
    MembershipCondition,
    OperandConvertibleWithIdentifier,
    RelationalCondition,
)


@final
class Measure(OperandConvertibleWithIdentifier[MeasureIdentifier]):
    """A measure is a mostly-numeric data value, computed on demand for aggregation purposes.

    Example:
        .. doctest::
            :hide:

            >>> session = getfixture("default_session")

        Copying a measure does not copy its attributes:

        >>> table = session.create_table("Example", data_types={"ID": "String"})
        >>> cube = session.create_cube(table)
        >>> m = cube.measures
        >>> m["Original"] = 1
        >>> m["Original"].description = "Test description"
        >>> m["Original"].folder = "Test folder"
        >>> m["Original"].formatter = "INT[test: #,###]"
        >>> m["Original"].visible = False
        >>> m["Copy"] = m["Original"]
        >>> print(m["Copy"].description)
        None
        >>> print(m["Copy"].folder)
        None
        >>> m["Copy"].formatter
        'INT[#,###]'
        >>> m["Copy"].visible
        True

        Redefining a measure resets its attributes:

        >>> m["Original"] = 2
        >>> print(m["Original"].description)
        None
        >>> print(m["Original"].folder)
        None
        >>> m["Original"].formatter
        'INT[#,###]'
        >>> m["Original"].visible
        True

    See Also:
        :class:`~atoti.measures.Measures` to define one.
    """

    def __init__(
        self,
        identifier: MeasureIdentifier,
        /,
        *,
        client: Client,
        cube_identifier: CubeIdentifier,
    ) -> None:
        self._client: Final = client
        self._cube_identifier: Final = cube_identifier
        self.__identifier: Final = identifier

    def _get_discovery_measure(self) -> DiscoveryMeasure:
        return (
            get_discovery(client=self._client)
            .cubes[self._cube_identifier.cube_name]
            .name_to_measure[self.name]
        )

    @property
    def data_type(self) -> DataType:
        """Type of the values the measure evaluates to."""
        if self._client._py4j_client is None:
            return "Object"

        # Replace this with a GraphQL query once the data type is added to the schema.
        return self._client._py4j_client.get_measure_data_type(
            self._identifier,
            cube_name=self._cube_identifier.cube_name,
        )

    @property
    def description(self) -> str | None:
        """Description of the measure.

        Example:
            .. doctest::
                :hide:

                >>> session = getfixture("default_session")

            >>> df = pd.DataFrame(
            ...     columns=["Product", "Price"],
            ...     data=[
            ...         ("phone", 560),
            ...         ("headset", 80),
            ...         ("watch", 250),
            ...     ],
            ... )
            >>> table = session.read_pandas(df, keys={"Product"}, table_name="Example")
            >>> cube = session.create_cube(table)
            >>> m = cube.measures
            >>> print(m["Price.SUM"].description)
            None
            >>> m["Price.SUM"].description = "The sum of the price"
            >>> m["Price.SUM"].description
            'The sum of the price'
            >>> del m["Price.SUM"].description
            >>> print(m["Price.SUM"].description)
            None

        """
        if self._client._py4j_client is None:
            return self._get_discovery_measure().description

        # Replace this with a GraphQL query once changes inside data model transactions are observable.
        return self._client._py4j_client.get_measure_description(
            self._identifier,
            cube_name=self._cube_identifier.cube_name,
        )

    @description.setter
    def description(self, value: str) -> None:
        self._set_description(value)

    @description.deleter
    def description(self) -> None:
        self._set_description(None)

    def _set_description(self, value: str | None) -> None:
        py4j_client = self._client._require_py4j_client()
        py4j_client.set_measure_description(
            self._identifier,
            value,
            cube_name=self._cube_identifier.cube_name,
        )
        py4j_client.publish_measures(self._cube_identifier.cube_name)

    @property
    def folder(self) -> str | None:
        """Folder of the measure.

        Folders can be used to group measures in the :guilabel:`Data model` UI component.

        Example:
            .. doctest::
                :hide:

                >>> session = getfixture("default_session")

            >>> df = pd.DataFrame(
            ...     columns=["Product", "Price"],
            ...     data=[
            ...         ("phone", 600.0),
            ...         ("headset", 80.0),
            ...         ("watch", 250.0),
            ...     ],
            ... )
            >>> table = session.read_pandas(df, keys={"Product"}, table_name="Example")
            >>> cube = session.create_cube(table)
            >>> m = cube.measures
            >>> print(m["Price.SUM"].folder)
            None
            >>> m["Price.SUM"].folder = "Prices"
            >>> m["Price.SUM"].folder
            'Prices'
            >>> del m["Price.SUM"].folder
            >>> print(m["Price.SUM"].folder)
            None

        """
        if self._client._py4j_client is None:
            return self._get_discovery_measure().folder

        # Replace this with a GraphQL query once changes inside data model transactions are observable.
        return self._client._py4j_client.get_measure_folder(
            self._identifier,
            cube_name=self._cube_identifier.cube_name,
        )

    @folder.setter
    def folder(self, value: str) -> None:
        self._set_folder(value)

    @folder.deleter
    def folder(self) -> None:
        self._set_folder(None)

    def _set_folder(self, value: str | None) -> None:
        py4j_client = self._client._require_py4j_client()
        py4j_client.set_measure_folder(
            self._identifier,
            value,
            cube_name=self._cube_identifier.cube_name,
        )
        py4j_client.publish_measures(self._cube_identifier.cube_name)

    @property
    def formatter(self) -> str | None:
        """Formatter of the measure.

        Note:
            The formatter only impacts how the measure is displayed, derived measures will still be computed from unformatted value.
            To round a measure, use :func:`atoti.math.round` instead.

        Example:
            .. doctest::
                :hide:

                >>> session = getfixture("default_session")

            >>> df = pd.DataFrame(
            ...     columns=["Product", "Price", "Quantity"],
            ...     data=[
            ...         ("phone", 559.99, 2),
            ...         ("headset", 79.99, 4),
            ...         ("watch", 249.99, 3),
            ...     ],
            ... )
            >>> table = session.read_pandas(df, keys={"Product"}, table_name="Example")
            >>> cube = session.create_cube(table)
            >>> h, l, m = cube.hierarchies, cube.levels, cube.measures
            >>> m["contributors.COUNT"].formatter
            'INT[#,###]'
            >>> m["contributors.COUNT"].formatter = "INT[count: #,###]"
            >>> m["contributors.COUNT"].formatter
            'INT[count: #,###]'
            >>> m["Price.SUM"].formatter
            'DOUBLE[#,###.00]'
            >>> m["Price.SUM"].formatter = "DOUBLE[$#,##0.00]"  # Add $ symbol
            >>> m["Ratio of sales"] = m["Price.SUM"] / tt.total(
            ...     m["Price.SUM"], h["Product"]
            ... )
            >>> m["Ratio of sales"].formatter
            'DOUBLE[#,###.00]'
            >>> m["Ratio of sales"].formatter = "DOUBLE[0.00%]"  # Percentage
            >>> m["Turnover in dollars"] = tt.agg.sum(
            ...     table["Price"] * table["Quantity"],
            ... )
            >>> m["Turnover in dollars"].formatter
            'DOUBLE[#,###.00]'
            >>> m["Turnover in dollars"].formatter = "DOUBLE[#,###]"  # Without decimals
            >>> cube.query(
            ...     m["contributors.COUNT"],
            ...     m["Price.SUM"],
            ...     m["Ratio of sales"],
            ...     m["Turnover in dollars"],
            ...     levels=[l["Product"]],
            ... )
                    contributors.COUNT Price.SUM Ratio of sales Turnover in dollars
            Product
            headset           count: 1    $79.99          8.99%                 320
            phone             count: 1   $559.99         62.92%               1,120
            watch             count: 1   $249.99         28.09%                 750

        The spec for the pattern between the ``DATE`` or ``DOUBLE``'s brackets is the one from `Microsoft Analysis Services <https://docs.microsoft.com/en-us/analysis-services/multidimensional-models/mdx/mdx-cell-properties-format-string-contents?view=asallproducts-allversions>`__.

        There is an extra formatter for array measures: ``ARRAY['|';1:3]`` where ``|`` is the separator used to join the elements of the ``1:3`` slice.
        """
        if self._client._py4j_client is None:
            return self._get_discovery_measure().format_string

        # Replace this with a GraphQL query once changes inside data model transactions are observable.
        return self._client._py4j_client.get_measure_formatter(
            self._identifier,
            cube_name=self._cube_identifier.cube_name,
        )

    @formatter.setter
    def formatter(self, value: str) -> None:
        py4j_client = self._client._require_py4j_client()
        py4j_client.set_measure_formatter(
            self._identifier,
            value,
            cube_name=self._cube_identifier.cube_name,
        )
        py4j_client.publish_measures(self._cube_identifier.cube_name)

    @property
    @override
    def _identifier(self) -> MeasureIdentifier:
        return self.__identifier

    @overload
    def isin(
        self,
        *values: Constant,
    ) -> (
        MembershipCondition[MeasureIdentifier, Literal["in"], Constant]
        | RelationalCondition[MeasureIdentifier, Literal["=="], Constant]
    ): ...

    @overload
    def isin(
        self,
        *values: Constant | None,
    ) -> (
        MembershipCondition[MeasureIdentifier, Literal["in"], Constant | None]
        | RelationalCondition[MeasureIdentifier, Literal["=="], Constant | None]
    ): ...

    def isin(
        self,
        *values: Constant | None,
    ) -> (
        MembershipCondition[MeasureIdentifier, Literal["in"], Constant | None]
        | RelationalCondition[MeasureIdentifier, Literal["=="], Constant | None]
    ):
        """Return a condition evaluating to ``True`` where this measure evaluates to one of the given *values*, and evaluating to ``False`` elsewhere.

        Args:
            values: One or more values that the measure will be compared against.

        Example:
            .. doctest::
                :hide:

                >>> session = getfixture("default_session")

            >>> df = pd.DataFrame(
            ...     columns=["City", "Price"],
            ...     data=[
            ...         ("Berlin", 150),
            ...         ("London", 270),
            ...         ("Madrid", 200),
            ...     ],
            ... )
            >>> table = session.read_pandas(df, keys={"City"}, table_name="Example")
            >>> cube = session.create_cube(table)
            >>> m = cube.measures
            >>> m["Price.SUM"].isin(150, 270)
            m['Price.SUM'].isin(150, 270)

            Conditions on single values are normalized to equality conditions:

            >>> m["Price.SUM"].isin(150)
            m['Price.SUM'] == 150

        """
        return MembershipCondition.of(
            subject=self._operation_operand,
            operator="in",
            elements=set(values),
        )

    @override
    def isnull(self) -> RelationalCondition[MeasureIdentifier, Literal["=="], None]:
        """Return a condition evaluating to ``True`` where this measure evalutes to ``None``, and evaluating to ``False`` elsewhere.

        Example:
            .. doctest::
                :hide:

                >>> session = getfixture("default_session")

            >>> df = pd.DataFrame(
            ...     columns=["City", "Price"],
            ...     data=[
            ...         ("Paris", 200.0),
            ...         ("Berlin", None),
            ...     ],
            ... )
            >>> table = session.read_pandas(df, table_name="Example")
            >>> cube = session.create_cube(table)
            >>> l, m = cube.levels, cube.measures
            >>> condition = m["Price.SUM"].isnull()
            >>> condition
            m['Price.SUM'].isnull()
            >>> m["Price.isnull"] = condition
            >>> m["Price.notnull"] = ~condition
            >>> cube.query(
            ...     m["Price.SUM"],
            ...     m["Price.isnull"],
            ...     m["Price.notnull"],
            ...     levels=[l["City"]],
            ... )
                   Price.SUM Price.isnull Price.notnull
            City
            Berlin                   True         False
            Paris     200.00        False          True

        """
        return RelationalCondition(
            subject=self._operation_operand, operator="==", target=None
        )

    @property
    def name(self) -> MeasureName:
        """Name of the measure."""
        return self._identifier.measure_name

    @property
    @override
    def _operation_operand(self) -> MeasureIdentifier:
        return self._identifier

    @property
    def visible(self) -> bool:
        """Whether the measure is visible or not.

        Example:
            .. doctest::
                :hide:

                >>> session = getfixture("default_session")

            >>> df = pd.DataFrame(
            ...     columns=["Product", "Price"],
            ...     data=[
            ...         ("phone", 560),
            ...         ("headset", 80),
            ...         ("watch", 250),
            ...     ],
            ... )
            >>> table = session.read_pandas(df, keys={"Product"}, table_name="Example")
            >>> cube = session.create_cube(table)
            >>> m = cube.measures
            >>> m["Price.SUM"].visible
            True
            >>> m["Price.SUM"].visible = False
            >>> m["Price.SUM"].visible
            False
            >>> m["contributors.COUNT"].visible
            True
            >>> m["contributors.COUNT"].visible = False
            >>> m["contributors.COUNT"].visible
            False
        """
        if self._client._py4j_client is None:
            return self._get_discovery_measure().visible

        # Replace this with a GraphQL query once changes inside data model transactions are observable.
        return self._client._py4j_client.get_measure_is_visible(
            self._identifier,
            cube_name=self._cube_identifier.cube_name,
        )

    @visible.setter
    def visible(self, value: bool) -> None:
        py4j_client = self._client._require_py4j_client()
        py4j_client.set_measure_visibility(
            self._identifier,
            value,
            cube_name=self._cube_identifier.cube_name,
        )
        py4j_client.publish_measures(self._cube_identifier.cube_name)
