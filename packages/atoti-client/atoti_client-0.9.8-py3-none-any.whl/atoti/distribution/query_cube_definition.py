from collections.abc import Set as AbstractSet
from dataclasses import KW_ONLY
from typing import final

from pydantic.dataclasses import dataclass

from .._base_cube_definition import BaseCubeDefinition
from .._identification import ApplicationNames, ClusterIdentifier, Identifiable
from .._identification.level_key import LevelUnambiguousKey
from .._pydantic import PYDANTIC_CONFIG as _PYDANTIC_CONFIG


@final
@dataclass(config=_PYDANTIC_CONFIG, frozen=True)
class QueryCubeDefinition(BaseCubeDefinition):
    """The definition to create a :class:`~atoti.QueryCube`."""

    cluster: Identifiable[ClusterIdentifier]
    """Cluster joined by the query cube."""

    _: KW_ONLY

    application_names: ApplicationNames | None = None
    """The names of the application allowed to contribute to the query cube.

    If ``None``, :attr:`cluster`'s :attr:`~atoti.ClusterDefinition.application_names` will be used.
    Otherwise, it must be a subset of that other set.

    :meta private:
    """

    distributing_levels: AbstractSet[LevelUnambiguousKey] = frozenset()
    """The :attr:`~atoti.QueryCube.distributing_levels`."""

    allow_data_duplication: bool = False
    """Whether to allow multiple data cubes in the same cluster to share some members in the :attr:`distributing_levels`.

    If ``True``, the priority of each data node can be configured when calling :meth:`atoti.Session.create_cube`.

    See the :atoti_server_docs:`Atoti Server docs <distributed/data_overlap/>` for more information.
    """
