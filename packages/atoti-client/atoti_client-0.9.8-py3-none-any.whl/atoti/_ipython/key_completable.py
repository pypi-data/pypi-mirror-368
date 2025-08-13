from abc import ABC, abstractmethod
from collections.abc import Collection
from typing import final


class KeyCompletable(ABC):
    @abstractmethod
    def _get_key_completions(self) -> Collection[str]: ...

    @final
    def _ipython_key_completions_(self) -> list[str]:
        # See https://ipython.readthedocs.io/en/stable/config/integrating.html#tab-completion.
        return sorted(self._get_key_completions())
