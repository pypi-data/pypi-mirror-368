from collections.abc import Callable
from typing import Final, final

from typing_extensions import override


@final
class AggregatesCache:
    def __init__(
        self,
        *,
        set_capacity: Callable[[int], None],
        get_capacity: Callable[[], int],
    ) -> None:
        self._set_capacity: Final = set_capacity
        self._get_capacity: Final = get_capacity

    @property
    def capacity(self) -> int:
        return self._get_capacity()

    @capacity.setter
    def capacity(self, capacity: int) -> None:
        self._set_capacity(capacity)

    @override
    def __repr__(self) -> str:
        return repr({"capacity": self.capacity})
