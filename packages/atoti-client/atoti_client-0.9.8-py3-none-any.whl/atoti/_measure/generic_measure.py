from typing import Final, final

from typing_extensions import override

from .._identification import MeasureIdentifier
from .._measure_definition import MeasureDefinition
from .._py4j_client import Py4jClient
from .utils import convert_measure_args


@final
class GenericMeasure(MeasureDefinition):
    def __init__(self, plugin_key: str, /, *args: object):
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
            *convert_measure_args(
                py4j_client=py4j_client,
                cube_name=cube_name,
                args=self._args,
            ),
            cube_name=cube_name,
        )
