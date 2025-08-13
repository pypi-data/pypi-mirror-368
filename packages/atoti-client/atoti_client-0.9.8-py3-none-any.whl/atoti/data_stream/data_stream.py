from abc import ABC, abstractmethod

from pydantic.dataclasses import dataclass

from .._pydantic import PYDANTIC_CONFIG as _PYDANTIC_CONFIG


@dataclass(config=_PYDANTIC_CONFIG, frozen=True)
class DataStream(ABC):
    """The definition of data that can be streamed into a table.

    The available implementations are:

    * :class:`atoti_kafka.KafkaStream`

    See Also:
        :meth:`~atoti.Table.stream`.

    """

    @property
    @abstractmethod
    def _options(
        self,
    ) -> dict[str, object]: ...

    @property
    @abstractmethod
    def _plugin_key(self) -> str: ...
