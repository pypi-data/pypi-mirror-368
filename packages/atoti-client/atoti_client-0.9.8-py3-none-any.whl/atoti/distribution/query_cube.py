from collections.abc import Set as AbstractSet
from typing import Final, final

from typing_extensions import override

from .._base_scenario_name import BASE_SCENARIO_NAME as _BASE_SCENARIO_NAME
from .._client import Client
from .._constant import Scalar
from .._graphql_client import UnloadMembersFromDataCubeInput
from .._identification import (
    HasIdentifier,
    Identifiable,
    LevelIdentifier,
    QueryCubeIdentifier,
    QueryCubeName,
    identify,
)
from .._identification.level_key import LevelUnambiguousKey
from .._ipython import ReprJson, ReprJsonable


# Only add methods and properties to this class if they are specific to query cubes.
# See comment in `BaseSession` for more information.
@final
class QueryCube(HasIdentifier[QueryCubeIdentifier], ReprJsonable):
    r"""A query cube of a :class:`~atoti.QuerySession`."""

    def __init__(self, identifier: QueryCubeIdentifier, /, *, client: Client):
        self._client: Final = client
        self.__identifier: Final = identifier

    @property
    @override
    def _identifier(self) -> QueryCubeIdentifier:
        return self.__identifier

    @property
    def name(self) -> QueryCubeName:
        """The name of the query cube."""
        return self._identifier.cube_name

    @property
    def distributing_levels(self) -> AbstractSet[LevelIdentifier]:
        """The identifiers of the levels distributing data across the data cubes connecting to the query cube.

        Each level is independently considered as a partitioning key.
        This means that for a query cube configured with ``distributing_levels={date_level_key, region_level_key}``, each data cube must contribute a unique :guilabel:`date`, not present in any other data cube, as well as a unique :guilabel:`region`.
        """
        levels = self._client._require_py4j_client().get_distributing_levels(
            self._identifier
        )
        return frozenset(
            LevelIdentifier._from_java_description(level_description)
            for level_description in levels
        )

    @property
    def data_cube_ids(self) -> AbstractSet[str]:
        """Opaque IDs representing each data cubes connected to this query cube."""
        output = self._client._require_graphql_client().get_cluster_members(
            cube_name=self.name
        )
        cluster = output.data_model.cube.cluster
        return (
            frozenset()
            if cluster is None
            else frozenset(node.name for node in cluster.nodes)
        )

    def unload_members_from_data_cube(
        self,
        members: AbstractSet[Scalar],
        *,
        data_cube_id: str,
        level: Identifiable[LevelIdentifier] | LevelUnambiguousKey,
        scenario_name: str = _BASE_SCENARIO_NAME,
    ) -> None:
        """Unload the given members of a level from a data cube.

        This is mostly used for data rollover.

        Note:
            This requires the query cube to have been created with :attr:`~atoti.QueryCubeDefinition.allow_data_duplication` set to ``True`` and with non empty :attr:`~atoti.QueryCubeDefinition.distributing_levels`.

        Args:
            members: The members to unload.
            data_cube_id: The ID of the data cube from which to unload the members.
                This must be equal to the *id_in_cluster* argument passed to :meth:`~atoti.Session.create_cube`.
            level: The level containing the members to unload.
            scenario_name: The name of the scenario from which facts must unloaded.

        Example:
            .. doctest::
                :hide:

                >>> from secrets import token_urlsafe
                >>> from tempfile import mkdtemp
                >>> from time import sleep
                >>> import pandas as pd
                >>> from atoti_jdbc import JdbcPingDiscoveryProtocol

            >>> application_name = "Cities"
            >>> cluster_name = "Cluster"
            >>> data_cube_id = "Europe"
            >>> query_cube_name = "Query cube"

            Setting up the :class:`query cube <atoti.QueryCube>`:

            >>> query_session = tt.QuerySession.start()
            >>> cluster_definition = tt.ClusterDefinition(
            ...     application_names={application_name},
            ...     discovery_protocol=JdbcPingDiscoveryProtocol(
            ...         f"jdbc:h2:{mkdtemp('atoti-cluster')}/db",
            ...         username="sa",
            ...         password="",
            ...     ),
            ...     authentication_token=token_urlsafe(),
            ... )
            >>> query_session.session.clusters[cluster_name] = cluster_definition
            >>> query_session.query_cubes[query_cube_name] = tt.QueryCubeDefinition(
            ...     query_session.session.clusters[cluster_name],
            ...     allow_data_duplication=True,
            ...     distributing_levels={(application_name, "City", "City")},
            ... )

            Defining some functions:

            >>> def query_by_city():
            ...     cube = query_session.session.cubes[query_cube_name]
            ...     l, m = cube.levels, cube.measures
            ...     return cube.query(m["Number.SUM"], levels=[l["City"]])

            >>> def wait_for_data(*, expected_city_count: int):
            ...     max_attempts = 30
            ...     for _ in range(max_attempts):
            ...         try:
            ...             result = query_by_city()
            ...             if len(result.index) == expected_city_count:
            ...                 return
            ...         except:
            ...             pass
            ...         sleep(1)
            ...     raise RuntimeError(f"Failed {max_attempts} attempts.")

            Setting up the :class:`data cube <atoti.Cube>`:

            >>> data_session = tt.Session.start()
            >>> data = pd.DataFrame(
            ...     columns=["City", "Number"],
            ...     data=[
            ...         ("Paris", 20.0),
            ...         ("London", 5.0),
            ...         ("Madrid", 7.0),
            ...     ],
            ... )
            >>> table = data_session.read_pandas(
            ...     data, keys={"City"}, table_name=application_name
            ... )
            >>> data_cube = data_session.create_cube(table, id_in_cluster=data_cube_id)

            Waiting for the data cube to join the cluster:

            >>> data_session.clusters[cluster_name] = cluster_definition
            >>> wait_for_data(expected_city_count=3)
            >>> query_by_city()
                   Number.SUM
            City
            London       5.00
            Madrid       7.00
            Paris       20.00

            Unloading the facts associated with the :guilabel:`London` and :guilabel:`Madrid` members:

            >>> query_session.query_cubes[
            ...     query_cube_name
            ... ].unload_members_from_data_cube(
            ...     {"London", "Madrid"},
            ...     data_cube_id=data_cube_id,
            ...     level=data_cube.levels["City"],
            ... )
            >>> wait_for_data(expected_city_count=1)
            >>> query_by_city()
                  Number.SUM
            City
            Paris      20.00

            .. doctest::
                :hide:

                >>> del data_session
                >>> del query_session

        """
        graphql_input = UnloadMembersFromDataCubeInput(
            branch_name=scenario_name,
            data_cube_id=data_cube_id,
            level_identifier=(
                LevelIdentifier.from_key(level)
                if isinstance(level, tuple)
                else identify(level)
            )._graphql_input,
            members=list(members),
            query_cube_name=self.name,
        )
        self._client._require_graphql_client().unload_members_from_data_cube(
            input=graphql_input
        )

    @override
    def _repr_json_(self) -> ReprJson:
        return (
            {"name": self.name},
            {"expanded": False, "root": self.name},
        )
