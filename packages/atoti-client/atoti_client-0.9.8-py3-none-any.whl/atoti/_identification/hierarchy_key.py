from typing import TypeAlias

from .dimension_name import DimensionName
from .hierarchy_name import HierarchyName

HierarchyUnambiguousKey: TypeAlias = tuple[DimensionName, HierarchyName]
HierarchyKey: TypeAlias = HierarchyName | HierarchyUnambiguousKey
