from __future__ import annotations

from collections import defaultdict
from collections.abc import Mapping, Set as AbstractSet
from typing import Final, final

from typing_extensions import override

from ._client import Client
from ._collections import DelegatingConvertingMapping, SupportsUncheckedMappingLookup
from ._cube_discovery import get_discovery
from ._graphql_client import DeleteMeasureInput, create_delete_status_validator
from ._identification import CubeIdentifier, MeasureIdentifier, MeasureName
from ._ipython import ReprJson, ReprJsonable
from ._measure_convertible import MeasureConvertible
from ._measure_definition import MeasureDefinition, convert_to_measure_definition
from .measure import Measure


@final
class Measures(
    SupportsUncheckedMappingLookup[MeasureName, MeasureName, Measure],
    DelegatingConvertingMapping[MeasureName, MeasureName, Measure, MeasureConvertible],
    ReprJsonable,
):
    """Manage the :class:`~atoti.Measure` of a :class:`~atoti.Cube`.

    The built-in measure :guilabel:`contributors.COUNT` counts how many rows from the cube's fact table contributed to each aggregate of a query:

    Example:
        .. doctest::
            :hide:

            >>> session = getfixture("default_session")

        >>> df = pd.DataFrame(
        ...     columns=["ID", "Continent", "Country", "City", "Color"],
        ...     data=[
        ...         (1, "Asia", "Japan", "Tokyo", "red"),
        ...         (2, "Asia", "Japan", "Kyoto", "red"),
        ...         (3, "Asia", "Singapore", "Singapore", "white"),
        ...         (4, "Europe", "Spain", "Madrid", "green"),
        ...         (5, "Europe", "Spain", "Barcelona", "blue"),
        ...     ],
        ... )
        >>> table = session.read_pandas(df, keys={"ID"}, table_name="Cities")
        >>> cube = session.create_cube(table, mode="manual")
        >>> h, l, m = cube.hierarchies, cube.levels, cube.measures
        >>> h["ID"] = [table["ID"]]
        >>> cube.query(m["contributors.COUNT"])
          contributors.COUNT
        0                  5
        >>> cube.query(m["contributors.COUNT"], levels=[l["ID"]], include_totals=True)
              contributors.COUNT
        ID
        Total                  5
        1                      1
        2                      1
        3                      1
        4                      1
        5                      1

        The caption of this measure can be changed with :class:`~atoti.I18nConfig`.

        A measure can evaluate to the current member of an expressed level:

        >>> h["Color"] = [table["Color"]]
        >>> m["Color"] = l["Color"]
        >>> cube.query(
        ...     m["Color"],
        ...     m["contributors.COUNT"],
        ...     levels=[l["Color"]],
        ...     include_totals=True,
        ... )
               Color contributors.COUNT
        Color
        Total                         5
        blue    blue                  1
        green  green                  1
        red      red                  2
        white  white                  1

        Or, for a multilevel hierarchy:

        >>> h["Geography"] = [table["Continent"], table["Country"], table["City"]]
        >>> m["Geography"] = h["Geography"]
        >>> cube.query(
        ...     m["Geography"],
        ...     m["contributors.COUNT"],
        ...     levels=[l["City"]],
        ...     include_totals=True,
        ... )
                                       Geography contributors.COUNT
        Continent Country   City
        Total                                                     5
        Asia                                Asia                  3
                  Japan                    Japan                  2
                            Kyoto          Kyoto                  1
                            Tokyo          Tokyo                  1
                  Singapore            Singapore                  1
                            Singapore  Singapore                  1
        Europe                            Europe                  2
                  Spain                    Spain                  2
                            Barcelona  Barcelona                  1
                            Madrid        Madrid                  1

        A measure can be compared to other objects, such as a constant, a :class:`~atoti.Level`, or another measure.
        If some condition inputs evaluate to ``None``, the resulting measure will evaluate to ``False``:

        >>> df = pd.DataFrame(
        ...     columns=["Product", "Quantity", "Threshold"],
        ...     data=[
        ...         ("bag", 5, 1),
        ...         ("car", 1, 5),
        ...         ("laptop", 4, None),
        ...         ("phone", None, 2),
        ...         ("watch", 3, 3),
        ...     ],
        ... )
        >>> table = session.read_pandas(df, keys={"Product"}, table_name="Products")
        >>> cube = session.create_cube(table)
        >>> l, m = cube.levels, cube.measures
        >>> m["Condition"] = m["Quantity.SUM"] > m["Threshold.SUM"]
        >>> cube.query(
        ...     m["Quantity.SUM"],
        ...     m["Threshold.SUM"],
        ...     m["Condition"],
        ...     levels=[l["Product"]],
        ...     include_totals=True,
        ... )
                Quantity.SUM Threshold.SUM Condition
        Product
        Total          13.00         11.00      True
        bag             5.00          1.00      True
        car             1.00          5.00     False
        laptop          4.00                   False
        phone                         2.00     False
        watch           3.00          3.00     False

        Measures can be defined and redefined without restarting the cube but, at the moment, deleting a measure will restart the cube so it will be slower:

        >>> m["test"] = 13  # no cube restart
        >>> m["test"] = 42  # no cube restart
        >>> del m["test"]  # cube restart

    See Also:
        * :mod:`atoti.agg`, :mod:`atoti.array`, :mod:`atoti.function`, :mod:`atoti.math`, and :mod:`atoti.string` for other ways to define measures.
        * :class:`~atoti.Measure` to configure existing measures.
    """

    def __init__(self, cube_identifier: CubeIdentifier, /, *, client: Client):
        self._client: Final = client
        self._cube_identifier: Final = cube_identifier

    @override
    def _create_lens(self, key: MeasureName, /) -> Measure:
        return Measure(
            MeasureIdentifier(key),
            client=self._client,
            cube_identifier=self._cube_identifier,
        )

    @override
    def _get_unambiguous_keys(self, *, key: MeasureName | None) -> list[MeasureName]:
        py4j_client = self._client._py4j_client

        if py4j_client is None:
            discovery = get_discovery(client=self._client)
            return [
                measure.name
                for measure in discovery.cubes[self._cube_identifier.cube_name].measures
                if key is None or measure.name == key
            ]

        if key is None:
            return py4j_client.get_measure_names(
                cube_name=self._cube_identifier.cube_name,
            )

        return [
            py4j_client.get_measure_name(
                MeasureIdentifier(key),
                cube_name=self._cube_identifier.cube_name,
            )
        ]

    @override
    def _update_delegate(
        self,
        other: Mapping[MeasureName, MeasureConvertible],
        /,
    ) -> None:
        py4j_client = self._client._require_py4j_client()

        for measure_name, measure in other.items():
            if not isinstance(measure, MeasureDefinition):
                measure = convert_to_measure_definition(measure)  # noqa: PLW2901

            try:
                measure._distil(
                    MeasureIdentifier(measure_name),
                    cube_name=self._cube_identifier.cube_name,
                    py4j_client=py4j_client,
                )
            except AttributeError as err:
                raise ValueError(f"Cannot create a measure from {measure}") from err

        py4j_client.publish_measures(self._cube_identifier.cube_name)

    @override
    def _delete_delegate_keys(self, keys: AbstractSet[MeasureName], /) -> None:
        graphql_client = self._client._require_graphql_client()

        with graphql_client.mutation_batcher.batch():
            for key in keys:
                graphql_input = DeleteMeasureInput(
                    cube_name=self._cube_identifier.cube_name,
                    measure_name=key,
                )
                graphql_client.delete_measure(input=graphql_input).set_output_validator(
                    create_delete_status_validator(
                        key, lambda output: output.delete_measure.status
                    )
                )

    @override
    def _repr_json_(self) -> ReprJson:
        measures_json: dict[str, dict[str, object]] = defaultdict(dict)
        no_folder = {}
        for measure in self.values():
            if measure.visible:
                json = {"formatter": measure.formatter}
                if measure.description is not None:
                    json["description"] = measure.description
                if measure.folder is None:
                    # We store them into another dict to insert them after the folders
                    no_folder[measure.name] = json
                else:
                    folder = f"📁 {measure.folder}"
                    measures_json[folder][measure.name] = json
        for folder, measures_in_folder in measures_json.items():
            measures_json[folder] = dict(sorted(measures_in_folder.items()))
        return (
            {**measures_json, **dict(sorted(no_folder.items()))},
            {"expanded": False, "root": "Measures"},
        )
