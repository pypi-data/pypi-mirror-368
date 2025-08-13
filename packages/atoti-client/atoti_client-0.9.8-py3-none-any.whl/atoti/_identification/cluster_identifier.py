from dataclasses import KW_ONLY
from typing import final

from pydantic.dataclasses import dataclass
from typing_extensions import override

from ._identifier_pydantic_config import IDENTIFIER_PYDANTIC_CONFIG
from .cluster_name import ClusterName
from .identifier import Identifier


@final
@dataclass(config=IDENTIFIER_PYDANTIC_CONFIG, frozen=True)
class ClusterIdentifier(Identifier):
    """The identifier of a :class:`~atoti.Cluster` in the context of a :class:`~atoti.Session`."""

    cluster_name: ClusterName
    _: KW_ONLY

    @override
    def __repr__(self) -> str:
        return f"""clusters[{self.cluster_name!r}]"""
