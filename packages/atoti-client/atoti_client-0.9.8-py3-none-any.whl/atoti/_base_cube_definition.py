from dataclasses import KW_ONLY

from pydantic.dataclasses import dataclass

from ._identification import CubeCatalogNames
from ._pydantic import PYDANTIC_CONFIG as _PYDANTIC_CONFIG


@dataclass(config=_PYDANTIC_CONFIG, frozen=True)
# Not `@final` because inherited by `CubeDefinition` and `QueryCubeDefinition`.
class BaseCubeDefinition:  # pylint: disable=final-class
    _: KW_ONLY

    catalog_names: CubeCatalogNames = frozenset({"atoti"})
    """The names of the catalogs in which the cube will be.

    :meta private:
    """
