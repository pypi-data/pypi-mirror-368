from __future__ import annotations

from collections.abc import Callable, Iterator, Mapping, MutableMapping, MutableSet
from typing import Annotated, Final, Literal, NoReturn, final, overload

from pydantic import Field, JsonValue
from typing_extensions import deprecated, override

from ._client import Client
from ._constant import ScalarT_co
from ._cube_discovery import get_discovery
from ._deprecated_warning_category import (
    DEPRECATED_WARNING_CATEGORY as _DEPRECATED_WARNING_CATEGORY,
)
from ._doc import doc
from ._graphql_client import UpdateHierarchyInput
from ._hierarchy_properties import HierarchyProperties
from ._hierarchy_viewers import HierarchyViewers
from ._identification import (
    CubeIdentifier,
    DimensionName,
    HasIdentifier,
    HierarchyIdentifier,
    HierarchyName,
    LevelIdentifier,
    LevelName,
    Role,
    check_not_reserved_dimension_name,
)
from ._ipython import ReprJson, ReprJsonable
from ._operation import HierarchyMembershipCondition, MembershipCondition
from ._operation.operation import RelationalCondition
from .level import Level

_FORCE_VIRTUAL_PROPERTY_NAME = "activeviam.experimental.forceVirtualHierarchies"
_VIRTUAL_HIERARCHY_CARDINALITY_THRESHOLD = 10_000


@final
class Hierarchy(
    Mapping[LevelName, Level],
    HasIdentifier[HierarchyIdentifier],
    ReprJsonable,
):
    """Hierarchy of a :class:`~atoti.Cube`.

    A hierarchy is a sub category of a :attr:`~dimension` and represents a precise type of data.

    For example, :guilabel:`Quarter` or :guilabel:`Week` could be hierarchies in the :guilabel:`Time` dimension.

    See Also:
        :class:`~atoti.hierarchies.Hierarchies` to define one.
    """

    def __init__(
        self,
        identifier: HierarchyIdentifier,
        /,
        *,
        client: Client,
        cube_identifier: CubeIdentifier,
    ) -> None:
        self._client: Final = client
        self._cube_identifier: Final = cube_identifier
        self.__identifier = identifier

    @final
    def __bool__(self) -> NoReturn:
        raise RuntimeError(
            "Hierarchies cannot be cast to a boolean. Use `.isin()` method or a relational operator to create a condition instead.",
        )

    @override
    def __hash__(self) -> int:
        # See comment in `OperandConvertible.__hash__()`.
        return id(self)

    @final
    @override
    # The signature is not compatible with `object.__eq__()` on purpose.
    def __eq__(  # type: ignore[override] # pyright: ignore[reportIncompatibleMethodOverride]
        self,
        other: ScalarT_co,  # type: ignore[misc]
        /,
    ) -> RelationalCondition[HierarchyIdentifier, Literal["=="], ScalarT_co]:
        assert other is not None, "Use `isnull()` instead."
        return RelationalCondition(
            subject=self._identifier, operator="==", target=other
        )

    @final
    @override
    # The signature is not compatible with `object.__ne__()` on purpose.
    def __ne__(  # type: ignore[override] # pyright: ignore[reportIncompatibleMethodOverride]
        self,
        other: ScalarT_co,  # type: ignore[misc]
        /,
    ) -> RelationalCondition[HierarchyIdentifier, Literal["!="], ScalarT_co]:
        assert other is not None, "Use `isnull()` instead."
        return RelationalCondition(
            subject=self._identifier, operator="!=", target=other
        )

    @property
    def dimension(self) -> DimensionName:
        """Name of the dimension of the hierarchy.

        A dimension is a logical group of attributes (e.g. :guilabel:`Geography`).
        It can be thought of as a folder containing hierarchies.

        Note:
            If all the hierarchies in a dimension have their deepest level of type ``TIME``, the dimension's type will be set to ``TIME`` too.
            This can be useful for some clients such as Excel which rely on the dimension's type to be ``TIME`` to decide whether to display date filters.
        """
        return self._identifier.dimension_identifier.dimension_name

    @dimension.setter
    def dimension(self, value: DimensionName, /) -> None:
        check_not_reserved_dimension_name(value)

        py4j_client = self._client._require_py4j_client()
        py4j_client.update_hierarchy_dimension(
            self._identifier,
            value,
            cube_name=self._cube_identifier.cube_name,
        )
        py4j_client.refresh()
        self.__identifier = HierarchyIdentifier.from_key((value, self.name))

    @property
    def dimension_default(self) -> bool:
        """Whether the hierarchy is the default in its :attr:`~atoti.Hierarchy.dimension` or not.

        Some UIs support clicking on a dimension (or drag and dropping it) as a shortcut to add its default hierarchy to a widget.

        Example:
            .. doctest::
                :hide:

                >>> session = getfixture("default_session")

            >>> table = session.create_table(
            ...     "Sales",
            ...     data_types={
            ...         "Product": "String",
            ...         "Shop": "String",
            ...         "Customer": "String",
            ...         "Date": "LocalDate",
            ...     },
            ... )
            >>> cube = session.create_cube(table, mode="manual")
            >>> h = cube.hierarchies
            >>> for column_name in table:
            ...     h[column_name] = [table[column_name]]
            ...     assert h[column_name].dimension == table.name

            By default, the default hierarchy of a dimension is the first created one:

            >>> h["Product"].dimension_default
            True
            >>> h["Shop"].dimension_default
            False
            >>> h["Customer"].dimension_default
            False
            >>> h["Date"].dimension_default
            False

            There can only be one default hierarchy per dimension:

            >>> h["Shop"].dimension_default = True
            >>> h["Product"].dimension_default
            False
            >>> h["Shop"].dimension_default
            True
            >>> h["Customer"].dimension_default
            False
            >>> h["Date"].dimension_default
            False

            When the default hierarchy is deleted, the first created remaining one becomes the default:

            >>> del h["Shop"]
            >>> h["Product"].dimension_default
            True
            >>> h["Customer"].dimension_default
            False
            >>> h["Date"].dimension_default
            False

            The same thing occurs if the default hierarchy is moved to another dimension:

            >>> h["Product"].dimension = "Product"
            >>> h["Customer"].dimension_default
            True
            >>> h["Date"].dimension_default
            False

            Since :guilabel:`Product` is the first created hierarchy of the newly created dimension, it is the default one there:

            >>> h["Product"].dimension_default
            True

        """
        graphql_client = self._client._graphql_client

        if graphql_client is None:
            discovery = get_discovery(client=self._client)
            return (
                discovery.cubes[self._cube_identifier.cube_name]
                .name_to_dimension[self.dimension]
                .default_hierarchy
                == self.name
            )

        output = graphql_client.get_dimension_default_hierarchy(
            cube_name=self._cube_identifier.cube_name,
            dimension_name=self.dimension,
        )
        return output.data_model.cube.dimension.default_hierarchy.name == self.name

    @dimension_default.setter
    def dimension_default(self, dimension_default: bool, /) -> None:
        py4j_client = self._client._require_py4j_client()
        py4j_client.set_hierarchy_dimension_default(
            self._identifier,
            dimension_default,
            cube_name=self._cube_identifier.cube_name,
        )
        py4j_client.refresh()
        self._dimension_default = dimension_default

    @property
    @override
    def _identifier(self) -> HierarchyIdentifier:
        return self.__identifier

    @overload
    def isin(
        self,
        *members: ScalarT_co,  # type: ignore[misc]
    ) -> (
        MembershipCondition[HierarchyIdentifier, Literal["in"], ScalarT_co]
        | RelationalCondition[HierarchyIdentifier, Literal["=="], ScalarT_co]
    ): ...

    @overload
    def isin(
        self,
        *member_paths: tuple[ScalarT_co, ...],
    ) -> HierarchyMembershipCondition[Literal["in"], ScalarT_co]: ...

    def isin(
        self,
        *members_or_member_paths: ScalarT_co | tuple[ScalarT_co, ...],
    ) -> (
        HierarchyMembershipCondition[Literal["in"], ScalarT_co]
        | MembershipCondition[HierarchyIdentifier, Literal["in"], ScalarT_co]
        | RelationalCondition[HierarchyIdentifier, Literal["=="], ScalarT_co]
    ):
        """Return a condition evaluating to ``True`` where this hierarchy's current member (or its path) is included in the given *members* (or *member_paths*), and evaluating to ``False`` elsewhere.

        Args:
            members_or_member_paths: Either:

                * One or more members.
                  In that case, all the hierarchy's members are expected to be unique across all the levels of the hierarchy.
                * One or more member paths expressed as tuples of members starting from the top of the hierarchy.

        Example:
            .. doctest::
                :hide:

                >>> session = getfixture("default_session")

            >>> df = pd.DataFrame(
            ...     columns=["Country", "City", "Price"],
            ...     data=[
            ...         ("Germany", "Berlin", 150.0),
            ...         ("Germany", "Hamburg", 120.0),
            ...         ("United Kingdom", "Bath", 240.0),
            ...         ("United Kingdom", "London", 270.0),
            ...     ],
            ... )
            >>> table = session.read_pandas(
            ...     df, keys={"Country", "City"}, table_name="Example"
            ... )
            >>> cube = session.create_cube(table, mode="manual")
            >>> h = cube.hierarchies
            >>> h["Geography"] = [table["Country"], table["City"]]

            Condition on members:

            >>> h["Geography"].isin("Germany", "London")
            h['Example', 'Geography'].isin('Germany', 'London')

            Condition on member paths:

            >>> h["Geography"].isin(("Germany",), ("United Kingdom", "Bath"))
            h['Example', 'Geography'].isin(('Germany',), ('United Kingdom', 'Bath'))

            Members and member paths cannot be mixed:

            >>> h["Geography"].isin("Germany", ("United Kingdom", "Bath"))
            Traceback (most recent call last):
                ...
            ValueError: Expected either only members or only member paths but both were mixed: `('Germany', ('United Kingdom', 'Bath'))`.

            Conditions on single members are normalized to equality conditions:

            >>> h["Geography"].isin("Germany")
            h['Example', 'Geography'] == 'Germany'

        """
        member_paths = frozenset(
            member_or_member_path
            for member_or_member_path in members_or_member_paths
            if isinstance(member_or_member_path, tuple)
        )
        if len(member_paths) == len(members_or_member_paths):
            return HierarchyMembershipCondition(
                subject=self._identifier,
                operator="in",
                member_paths=member_paths,
                level_names=list(self),
            )

        members = frozenset(
            member_or_member_path
            for member_or_member_path in members_or_member_paths
            if not isinstance(member_or_member_path, tuple)
        )
        if len(members) != len(members_or_member_paths):
            raise ValueError(
                f"Expected either only members or only member paths but both were mixed: `{members_or_member_paths}`."
            )

        return MembershipCondition.of(
            subject=self._identifier, operator="in", elements=members
        )

    def _get_level_names(self, *, key: LevelName | None) -> list[LevelName]:
        graphql_client = self._client._graphql_client

        # Remove `self._client._py4j_client is None` once `QuerySession`s are supported.
        if self._client._py4j_client is None or graphql_client is None:
            discovery = get_discovery(client=self._client)
            return [
                level.name
                for level in discovery.cubes[self._cube_identifier.cube_name]
                .name_to_dimension[self.dimension]
                .name_to_hierarchy[self.name]
                .levels
                if level.type != "ALL" and (key is None or level.name == key)
            ]

        if key is None:
            output = graphql_client.get_hierarchy_levels(
                cube_name=self._cube_identifier.cube_name,
                dimension_name=self.dimension,
                hierarchy_name=self.name,
            )
            levels = output.data_model.cube.dimension.hierarchy.levels
            return [level.name for level in levels if level.type.value != "ALL"]

        output = graphql_client.find_level_in_hierarchy(  # type: ignore[assignment] # See https://github.com/python/mypy/issues/12968.
            cube_name=self._cube_identifier.cube_name,
            dimension_name=self.dimension,
            hierarchy_name=self.name,
            level_name=key,
        )
        level = output.data_model.cube.dimension.hierarchy.level  # type: ignore[attr-defined]
        return [level.name] if level and level.type.value != "ALL" else []

    @property
    @deprecated(
        "`Hierarchy.levels` is deprecated, iterate on the hierarchy instead.",
        category=_DEPRECATED_WARNING_CATEGORY,
    )
    def levels(self) -> Mapping[str, Level]:
        """Levels of the hierarchy.

        :meta private:
        """
        return {
            level_name: Level(
                LevelIdentifier(self._identifier, level_name),
                client=self._client,
                cube_identifier=self._cube_identifier,
            )
            for level_name in self._get_level_names(key=None)
        }

    @override
    def __getitem__(self, key: LevelName, /) -> Level:
        level_names = self._get_level_names(key=key)
        if not level_names:
            raise KeyError(key)
        assert len(level_names) == 1
        return Level(
            LevelIdentifier(self._identifier, level_names[0]),
            client=self._client,
            cube_identifier=self._cube_identifier,
        )

    @override
    def __iter__(self) -> Iterator[LevelName]:
        return iter(self._get_level_names(key=None))

    @override
    def __len__(self) -> int:
        return len(self._get_level_names(key=None))

    @property
    def name(self) -> HierarchyName:
        """Name of the hierarchy."""
        return self._identifier.hierarchy_name

    @property
    def _properties(self) -> MutableMapping[str, JsonValue]:
        return HierarchyProperties(
            self._identifier,
            client=self._client,
            cube_identifier=self._cube_identifier,
        )

    @override
    def _repr_json_(self) -> ReprJson:
        root = f"{self.name}{' (slicing)' if self.slicing else ''}"
        return (
            list(self),
            {
                "root": root,
                "expanded": False,
            },
        )

    @property
    def slicing(self) -> bool:
        """Whether the hierarchy is slicing or not.

        * A regular (i.e. non-slicing) hierarchy is considered aggregable, meaning that it makes sense to aggregate data across all members of the hierarchy.

          For instance, for a :guilabel:`Geography` hierarchy, it is useful to see the worldwide aggregated :guilabel:`Turnover` across all countries.

        * A slicing hierarchy is not aggregable at the top level, meaning that it does not make sense to aggregate data across all members of the hierarchy.

          For instance, for an :guilabel:`As of date` hierarchy giving the current bank account :guilabel:`Balance` for a given date, it does not provide any meaningful information to aggregate the :guilabel:`Balance` across all the dates.
        """
        # Remove `self._client._py4j_client is None` once `QuerySession`s are supported.
        if self._client._py4j_client is None or self._client._graphql_client is None:
            discovery = get_discovery(client=self._client)
            return (
                discovery.cubes[self._cube_identifier.cube_name]
                .name_to_dimension[self.dimension]
                .name_to_hierarchy[self.name]
                .slicing
            )

        output = self._client._graphql_client.get_hierarchy_is_slicing(
            cube_name=self._cube_identifier.cube_name,
            dimension_name=self.dimension,
            hierarchy_name=self.name,
        )
        return output.data_model.cube.dimension.hierarchy.is_slicing

    @slicing.setter
    def slicing(self, value: bool, /) -> None:
        py4j_client = self._client._require_py4j_client()
        py4j_client.update_hierarchy_slicing(
            self._identifier,
            value,
            cube_name=self._cube_identifier.cube_name,
        )
        py4j_client.refresh()

    @property
    @doc(
        cardinality_threshold=str(_VIRTUAL_HIERARCHY_CARDINALITY_THRESHOLD),
        force_property_name=_FORCE_VIRTUAL_PROPERTY_NAME,
    )
    def virtual(self) -> bool | None:
        r"""Whether the hierarchy is virtual or not.

        A virtual hierarchy does not store in memory the list of its members.
        Hierarchies with large cardinality are good candidates for being virtual.

        By default, a given hierarchy is automatically set as virtual if and only if it comes from an :class:`~atoti.ExternalTable` and one of the following conditions is met:

        * The hierarchy has a cardinality of {cardinality_threshold} or more;
        * The ``{force_property_name}`` property is set to ``true``.

        Note:
            As its name suggests, ``{force_property_name}`` is an experimental/temporary property which may change in future bugfix releases.

        Example:
            .. doctest::
                :hide:

                >>> clickhouse_server_port = getfixture("clickhouse_server_port")
                >>> schema_name = "tck_db_v1"

            >>> from atoti_directquery_clickhouse import ConnectionConfig, TableConfig
            >>> connection_config = ConnectionConfig(
            ...     url=f"clickhouse:http://localhost:{{clickhouse_server_port}}/{{schema_name}}",
            ... )
            >>> table_config = TableConfig(keys={{"id"}})

            * Without ``{force_property_name}``:

              >>> session = tt.Session.start()
              >>> external_database = session.connect_to_external_database(
              ...     connection_config
              ... )
              >>> sales_table = session.add_external_table(
              ...     external_database.tables["sales"], config=table_config
              ... )
              >>> cube = session.create_cube(sales_table)
              >>> cube.hierarchies["product"].virtual
              False

            * With ``{force_property_name}``:

              >>> session_config = tt.SessionConfig(
              ...     java_options=["-D{force_property_name}=true"]
              ... )
              >>> session = tt.Session.start(session_config)
              >>> external_database = session.connect_to_external_database(
              ...     connection_config
              ... )
              >>> sales_table = session.add_external_table(
              ...     external_database.tables["sales"], config=table_config
              ... )
              >>> cube = session.create_cube(sales_table)
              >>> cube.hierarchies["product"].virtual
              True

            .. doctest::
                :hide:

                >>> ASqlDatabaseManager = session._client._require_py4j_client().jvm.io.atoti.runtime.private_.directquery.sql.ASqlDatabaseManager
                >>> assert (
                ...     int("{cardinality_threshold}")
                ...     == ASqlDatabaseManager.VIRTUAL_HIERARCHY_LIMIT
                ... )
                >>> assert (
                ...     "{force_property_name}"
                ...     == ASqlDatabaseManager.FORCE_VIRTUAL_HIERARCHIES_PROPERTY
                ... )
                >>> del session
        """
        # Remove `self._client._py4j_client is None` once `QuerySession`s are supported.
        if self._client._py4j_client is None or self._client._graphql_client is None:
            return None

        output = self._client._graphql_client.get_hierarchy_is_virtual(
            cube_name=self._cube_identifier.cube_name,
            dimension_name=self.dimension,
            hierarchy_name=self.name,
        )
        return output.data_model.cube.dimension.hierarchy.is_virtual

    @virtual.setter
    def virtual(self, virtual: bool, /) -> None:
        py4j_client = self._client._require_py4j_client()
        py4j_client.update_hierarchy_virtual(
            self._identifier,
            virtual,
            cube_name=self._cube_identifier.cube_name,
        )
        py4j_client.refresh()

    @property
    def visible(self) -> bool:
        """Whether the hierarchy should be displayed to the user in Atoti UI (or other compatible clients).

        Note:
            This is not a security feature: users will still be able to query the hierarchy even if it is not visible to them.

        See Also:
            :attr:`viewers`.

        """
        # Remove `self._client._py4j_client is None` once `QuerySession`s are supported.
        if self._client._py4j_client is None or self._client._graphql_client is None:
            discovery = get_discovery(client=self._client)
            return (
                discovery.cubes[self._cube_identifier.cube_name]
                .name_to_dimension[self.dimension]
                .name_to_hierarchy[self.name]
                .visible
            )

        output = self._client._graphql_client.get_hierarchy_is_visible(
            cube_name=self._cube_identifier.cube_name,
            dimension_name=self.dimension,
            hierarchy_name=self.name,
        )
        return output.data_model.cube.dimension.hierarchy.is_visible

    @visible.setter
    @deprecated(
        "`Hierarchy.visible` setter is deprecated, use `Hierarchy.viewers` instead.",
    )
    def visible(self, value: bool, /) -> None:
        self.viewers.clear()
        if value:
            self.viewers.add("ROLE_USER")

    @property
    def folder(self) -> str | None:
        r"""The hierarchy folder.

        Example:
            .. doctest::
                :hide:

                >>> session = getfixture("default_session")

        >>> table = session.create_table("Example", data_types={"Product": "String"})
        >>> cube = session.create_cube(table)
        >>> hierarchy = cube.hierarchies["Product"]

        By convention, the :guilabel:`\\` separator denotes nesting:

        >>> hierarchy.folder = r"some\sub\folder"
        >>> print(hierarchy.folder)
        some\sub\folder

        >>> del hierarchy.folder
        >>> print(hierarchy.folder)
        None
        """
        if self._client._py4j_client is None or self._client._graphql_client is None:
            discovery = get_discovery(client=self._client)
            return (
                discovery.cubes[self._cube_identifier.cube_name]
                .name_to_dimension[self.dimension]
                .name_to_hierarchy[self.name]
                .folder
            )

        output = self._client._graphql_client.get_hierarchy_folder(
            cube_name=self._cube_identifier.cube_name,
            dimension_name=self.dimension,
            hierarchy_name=self.name,
        )

        return output.data_model.cube.dimension.hierarchy.folder

    @folder.setter
    def folder(self, value: Annotated[str, Field(min_length=1)], /) -> None:
        def update_input(update_hierarchy_input: UpdateHierarchyInput, /) -> None:
            update_hierarchy_input.folder = value

        self._update(update_input)

    @folder.deleter
    def folder(self) -> None:
        def update_input(update_hierarchy_input: UpdateHierarchyInput, /) -> None:
            update_hierarchy_input.folder = None

        self._update(update_input)

    @property
    def members_indexed_by_name(self) -> bool:
        """Whether the hierarchy maintains an index of its members by name.

        :meta private:
        """
        output = self._client._require_graphql_client().get_hierarchy_are_members_indexed_by_name(
            cube_name=self._cube_identifier.cube_name,
            dimension_name=self.dimension,
            hierarchy_name=self.name,
        )
        return output.data_model.cube.dimension.hierarchy.are_members_indexed_by_name

    @members_indexed_by_name.setter
    def members_indexed_by_name(self, value: bool, /) -> None:
        def update_input(update_hierarchy_input: UpdateHierarchyInput, /) -> None:
            update_hierarchy_input.are_members_indexed_by_name = value

        self._update(update_input)

    @property
    def viewers(self) -> MutableSet[Role]:
        """:attr:`~atoti.Hierarchy.visible` is `True` if and only if at least one of the roles of the current user is included in this set.

        Example:
            * Without security:

              .. doctest::
                :hide:

                >>> session = getfixture("default_session")

              >>> table = session.create_table(
              ...     "Example", data_types={"Product": "String"}
              ... )
              >>> cube = session.create_cube(table)
              >>> hierarchy = cube.hierarchies["Product"]

              Each hierarchy is visible by default:

              >>> hierarchy.viewers
              {'ROLE_USER'}
              >>> hierarchy.visible
              True

              Hiding the hierarchy from all users:

              >>> hierarchy.viewers.clear()
              >>> hierarchy.viewers
              set()
              >>> hierarchy.visible
              False

            * With security:

              >>> session_config = tt.SessionConfig(security=tt.SecurityConfig())
              >>> secured_session = tt.Session.start(session_config)
              >>> table = secured_session.create_table(
              ...     "Example", data_types={"Product": "String"}
              ... )
              >>> cube = secured_session.create_cube(table)
              >>> hierarchy = cube.hierarchies["Product"]

              Each hierarchy is visible by default:

              >>> hierarchy.viewers
              {'ROLE_USER'}
              >>> hierarchy.visible
              True

              Setting up a non-admin user:

              >>> authentication = tt.BasicAuthentication("John", "passwd")
              >>> secured_session.security.individual_roles[authentication.username] = {
              ...     "ROLE_USER"
              ... }
              >>> secured_session.security.basic_authentication.credentials[
              ...     authentication.username
              ... ] = authentication.password
              >>> john_session = tt.Session.connect(
              ...     secured_session.url, authentication=authentication
              ... )

              John has :guilabel:`ROLE_USER` which is in :attr:`viewers` so the hierarchy is visible to him:

              >>> hierarchy_seen_by_john = john_session.cubes["Example"].hierarchies[
              ...     "Product"
              ... ]
              >>> hierarchy_seen_by_john.visible
              True

              Hiding the hierarchy from all users:

              >>> hierarchy.viewers.clear()
              >>> hierarchy.viewers
              set()
              >>> hierarchy.visible
              False
              >>> hierarchy_seen_by_john.visible
              False

              Making the hierarchy visible to admins only:

              >>> hierarchy.viewers.add("ROLE_ADMIN")
              >>> hierarchy.viewers
              {'ROLE_ADMIN'}
              >>> hierarchy.visible
              True
              >>> hierarchy_seen_by_john.visible
              False

              .. doctest::
                  :hide:

                  >>> del john_session
                  >>> del secured_session

        """
        return HierarchyViewers(
            cube_name=self._cube_identifier.cube_name,
            hierarchy_identifier=self._identifier,
            client=self._client,
        )

    def _update(self, update_input: Callable[[UpdateHierarchyInput], None], /) -> None:
        graphql_input = UpdateHierarchyInput(
            cube_name=self._cube_identifier.cube_name,
            hierarchy_identifier=self._identifier._graphql_input,
        )
        update_input(graphql_input)
        self._client._require_graphql_client().update_hierarchy(input=graphql_input)
