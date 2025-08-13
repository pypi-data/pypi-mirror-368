from collections.abc import Set as AbstractSet
from typing import Annotated, final

from pydantic import AfterValidator, Field, model_validator
from pydantic.dataclasses import dataclass
from typing_extensions import Self

from ._identification import (
    HierarchyIdentifier,
    Identifiable,
    LevelIdentifier,
    Role,
    identify,
)
from ._pydantic import PYDANTIC_CONFIG as _PYDANTIC_CONFIG
from ._validate_hierarchy_unicity import validate_hierarchy_unicity


@final
@dataclass(config=_PYDANTIC_CONFIG, frozen=True, kw_only=True)
class UpdateableCells:
    """Updateable cells configuration is used to define the cells that can be updated by users.

    Example:
        .. doctest::
            :hide:

            >>> import atoti._updateable_cells
            >>> session = getfixture("default_session")

        >>> data = pd.DataFrame(
        ...     columns=["City", "Currency", "Price"],
        ...     data=[
        ...         ("Paris", "EUR", 200),
        ...         ("London", "GBP", 100),
        ...         ("Berlin", "EUR", 300),
        ...         ("NYC", "USD", 150),
        ...     ],
        ... )
        >>> table = session.read_pandas(data, keys={"City"}, table_name="Prices")
        >>> cube = session.create_cube(table)
        >>> h, l = cube.hierarchies, cube.levels
        >>> cube.updateable_cells
        >>> None
        >>> cube.updateable_cells = atoti._updateable_cells.UpdateableCells(
        ...     hierarchies={h["City"]},
        ...     levels={l["Currency"]},
        ...     roles={"ROLE_ADMIN"},
        ... )
        >>> cube.updateable_cells
        UpdateableCells(hierarchies=frozenset({h['Prices', 'City']}), levels=frozenset({l['Prices', 'Currency', 'Currency']}), roles=frozenset({'ROLE_ADMIN'}))
        >>> del cube.updateable_cells
        >>> print(cube.updateable_cells)
        None

    """

    hierarchies: AbstractSet[Identifiable[HierarchyIdentifier]] = frozenset()
    """The hierarchies on which members must be leaves to be updateable."""

    levels: Annotated[
        AbstractSet[Identifiable[LevelIdentifier]],
        AfterValidator(validate_hierarchy_unicity),
    ] = frozenset()
    """The levels defining the threshold depths at which their hierarchy becomes updateable."""

    roles: Annotated[AbstractSet[Role], Field(min_length=1)]
    """The roles allowed to update cells."""

    @model_validator(mode="after")  # type: ignore[misc]
    def validate_hierarchy_and_level_unicity(self) -> Self:
        duplicated_hierarchy_identifiers = {
            identify(hierarchy) for hierarchy in self.hierarchies
        } & {identify(level).hierarchy_identifier for level in self.levels}
        if duplicated_hierarchy_identifiers:
            raise ValueError(
                f"The hierarchies {duplicated_hierarchy_identifiers} are duplicated between `hierarchies` and `levels`."
            )
        return self
