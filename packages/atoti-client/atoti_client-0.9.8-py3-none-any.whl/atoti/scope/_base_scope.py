from abc import ABC, abstractmethod

from .._measure_convertible import VariableMeasureConvertible
from .._measure_definition import MeasureDefinition


# Do not make this type public unless also renaming it to `Scope` and getting rid of the existing `Scope` union.
class BaseScope(ABC):
    @abstractmethod
    def _create_measure_definition(
        self,
        measure: VariableMeasureConvertible,
        /,
        *,
        plugin_key: str,
    ) -> MeasureDefinition: ...
