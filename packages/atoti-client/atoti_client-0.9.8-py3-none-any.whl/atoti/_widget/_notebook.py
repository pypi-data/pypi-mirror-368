from __future__ import annotations

from functools import cache
from typing import TYPE_CHECKING, Any, Final, final

from .._ipython import get_ipython
from ._notebook_cell import NotebookCell

if TYPE_CHECKING:
    from ipykernel.ipkernel import (  # pylint: disable=nested-import,undeclared-dependency
        IPythonKernel,
    )


@final
class Notebook:
    @cache
    @staticmethod
    def current() -> Notebook | None:
        ipython = get_ipython()

        if ipython is None:
            return None

        kernel = getattr(ipython, "kernel", None)

        if kernel is None or not hasattr(kernel, "comm_manager"):
            # When run from IPython or another less elaborated environment than JupyterLab, these attributes might be missing.
            # In that case, there is no need to register anything.
            return None

        notebook = Notebook(kernel=kernel)
        notebook.wrap_execute_request_handler_to_extract_widget_details()
        return notebook

    def __init__(self, *, kernel: IPythonKernel) -> None:
        self._current_cell: NotebookCell | None = None
        self._kernel: Final = kernel

    @property
    def current_cell(self) -> NotebookCell | None:
        return self._current_cell

    def wrap_execute_request_handler_to_extract_widget_details(
        self,
        /,
    ) -> None:
        original_handler = self._kernel.shell_handlers["execute_request"]

        def execute_request(  # pylint: disable=too-many-positional-parameters
            stream: Any,
            ident: Any,
            parent: Any,
        ) -> Any:
            metadata = parent["metadata"]
            cell_id = metadata.get("cellId")
            self._current_cell = (
                None
                if cell_id is None
                else NotebookCell(
                    has_built_widget=bool(metadata.get("atoti", {}).get("state")),
                    id=cell_id,
                )
            )

            return original_handler(stream, ident, parent)

        self._kernel.shell_handlers["execute_request"] = execute_request
