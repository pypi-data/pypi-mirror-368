from collections.abc import Callable, Mapping
from typing import Final, final
from uuid import uuid4

from typing_extensions import override

from .._mime_type import TEXT_MIME_TYPE, WIDGET_MIME_TYPE
from ._notebook import Notebook
from ._widget_comm_target_name import WIDGET_COMM_TARGET_NAME

_NOTEBOOK = Notebook.current()


@final
class Widget:
    def __init__(
        self,
        *,
        block_until_loaded: Callable[[str], None],
        get_authentication_headers: Callable[[], Mapping[str, str]],
        get_creation_code: Callable[[], str | None],
        session_id: str,
        session_url: str,
    ) -> None:
        self.block_until_loaded: Final = block_until_loaded
        self.get_authentication_headers: Final = get_authentication_headers
        self.get_creation_code: Final = get_creation_code
        self.session_id: Final = session_id
        self.session_url: Final = session_url

    def _ipython_display_(self) -> None:
        if not _NOTEBOOK:
            print(self)  # noqa: T201
            return

        from ipykernel.comm import (  # pylint: disable=nested-import,undeclared-dependency
            Comm,
        )
        from IPython.display import (  # pylint: disable=nested-import,undeclared-dependency
            publish_display_data,
        )

        cell = _NOTEBOOK.current_cell

        data: dict[str, object] = {
            TEXT_MIME_TYPE: f"""Open the notebook in JupyterLab with the Atoti JupyterLab extension enabled to {"see" if cell and cell.has_built_widget else "build"} this widget.""",
        }

        widget_creation_code = self.get_creation_code()

        if widget_creation_code:
            data[WIDGET_MIME_TYPE] = {
                "sessionId": self.session_id,
                "sessionUrl": self.session_url,
                "widgetCreationCode": widget_creation_code,
            }

        # Mypy cannot find the type of this function.
        publish_display_data(data)  # type: ignore[no-untyped-call]

        if cell is None:
            return

        widget_id = str(uuid4())

        # Mypy cannot find the type of this class.
        Comm(  # type: ignore[no-untyped-call]
            WIDGET_COMM_TARGET_NAME,
            # The data below is either sensitive (e.g. authentication headers) or change from one cell run to the other.
            # It is better to not send it through publish_display_data so that it does not end up in the .ipynb file.
            data={
                "cellId": cell.id,
                "sessionHeaders": {**self.get_authentication_headers()},
                "widgetId": widget_id,
            },
        ).close()

        self.block_until_loaded(widget_id)

    @override
    def __repr__(self) -> str:
        return "Widgets can only be displayed in JupyterLab with atoti-jupyterlab installed."
