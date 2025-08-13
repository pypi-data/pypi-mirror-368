from collections.abc import Mapping, Sequence
from typing import Any, Final, TypeAlias, final

from typing_extensions import override

from .._constant import Scalar
from .._identification import (
    HasIdentifier,
    MeasureIdentifier,
)
from .._measure_definition import MeasureDefinition
from .._py4j_client import Py4jClient
from .utils import convert_plugin_measure_args

PluginMeasureArgs: TypeAlias = Scalar | HasIdentifier[Any]

SequencePluginMeasureArgs: TypeAlias = (
    Sequence[PluginMeasureArgs]
    | PluginMeasureArgs
    | Mapping[str, PluginMeasureArgs]
    | Mapping[str, Sequence[PluginMeasureArgs]]
)

NestedPluginMeasureArgs: TypeAlias = (
    PluginMeasureArgs
    | SequencePluginMeasureArgs
    | Sequence[SequencePluginMeasureArgs]
    | Mapping[str, SequencePluginMeasureArgs]
)


@final
class PluginMeasure(MeasureDefinition):
    def __init__(self, plugin_key: str, /, *args: NestedPluginMeasureArgs):
        """Create the measure.

        Args:
            args: The arguments used to create the measure.
                They are directly forwarded to the Java code, except for the ``Measure``
                arguments that are first created on the Java side and replaced by their name.
            plugin_key: The plugin key of the Java implementation.
        """
        self._args: Final = args
        self._plugin_key: Final = plugin_key

    @override
    def _do_distil(
        self,
        identifier: MeasureIdentifier | None = None,
        /,
        *,
        cube_name: str,
        py4j_client: Py4jClient,
    ) -> MeasureIdentifier:
        return py4j_client.create_measure(
            identifier,
            self._plugin_key,
            *convert_plugin_measure_args(
                py4j_client=py4j_client,
                args=self._args,
            ),
            cube_name=cube_name,
        )
