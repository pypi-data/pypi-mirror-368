from dataclasses import KW_ONLY
from types import EllipsisType
from typing import Annotated, Literal, TypeAlias, final

from pydantic import Field
from pydantic.dataclasses import dataclass

from ._base_cube_definition import BaseCubeDefinition
from ._cube_filter_condition import CubeFilterCondition
from ._identification import (
    ApplicationName,
    CubeCatalogNames,
    Identifiable,
    TableIdentifier,
)
from ._pydantic import PYDANTIC_CONFIG as _PYDANTIC_CONFIG

_CreationMode: TypeAlias = Literal["auto", "manual"]


@final
@dataclass(config=_PYDANTIC_CONFIG, frozen=True)
class CubeDefinition(BaseCubeDefinition):
    """The definition to create a :class:`~atoti.Cube`.

    Example:
        .. doctest::
            :hide:

            >>> session = getfixture("default_session")

        >>> table = session.create_table(
        ...     "Table",
        ...     data_types={"id": "String", "value": "double"},
        ... )

        Auto hierarchies and measures:

        >>> definition = CubeDefinition(table)
        >>> cube = session.cubes.set(table.name, definition)
        >>> sorted(cube.measures)
        ['contributors.COUNT', 'update.TIMESTAMP', 'value.MEAN', 'value.SUM']
        >>> list(cube.hierarchies)
        [('Table', 'id')]

        Auto hierarchies and manual measures:

        >>> definition = CubeDefinition(table, measures="manual")
        >>> cube = session.cubes.set(table.name, definition)
        >>> sorted(cube.measures)
        ['contributors.COUNT', 'update.TIMESTAMP']
        >>> list(cube.hierarchies)
        [('Table', 'id')]

        Manual hierarchies and measures:

        >>> definition = CubeDefinition(table, hierarchies="manual", measures="manual")
        >>> cube = session.cubes.set(table.name, definition)
        >>> sorted(cube.measures)
        ['contributors.COUNT', 'update.TIMESTAMP']
        >>> list(cube.hierarchies)
        []

    """

    fact_table: Identifiable[TableIdentifier]
    """The table containing the facts of the cube."""

    _: KW_ONLY

    application_name: ApplicationName | EllipsisType | None = None
    """The name of the application this data cube contributes to.

    If ``...``, the cube name will be used.
    """

    catalog_names: CubeCatalogNames = frozenset({"atoti"})
    """The names of the catalogs in which the cube will be.

    :meta private:
    """

    filter: CubeFilterCondition | None = None

    hierarchies: _CreationMode = "auto"
    """How hierarchies will be created.

    If ``"auto"``, hierarchies will be created for every :attr:`key column <atoti.Table.keys>` or non-numeric column of :attr:`fact_table`.
    """

    id_in_cluster: str | None = None
    """The human-friendly name used to identify this data cube within a cluster."""

    measures: _CreationMode = "auto"
    """How measures will be created.

    If ``"auto"``, measures will be created for every numeric column of :attr:`fact_table`.
    """

    priority: Annotated[int, Field(gt=0)] | None = None
    """The priority of this data cube when using distribution with data overlap.

    If no priority is defined, duplicated data is retrieved in priority from the node with the fewest members of distributing levels.
    """
