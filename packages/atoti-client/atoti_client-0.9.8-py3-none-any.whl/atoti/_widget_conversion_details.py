from dataclasses import dataclass
from importlib.metadata import version
from typing import final

from ._session_id import SessionId


@final
@dataclass(frozen=True, kw_only=True)
class WidgetConversionDetails:
    mdx: str
    # This class is used in the JupyterLab extension written in JavaScript.
    # JavaScript uses camelCase.
    sessionId: SessionId  # noqa: N815
    widgetCreationCode: str  # noqa: N815


_MAJOR_VERSION = version("atoti-client").split(".", maxsplit=1)[0]

CONVERT_MDX_QUERY_RESULT_TO_WIDGET_MIME_TYPE = (
    f"application/vnd.atoti.convert-mdx-query-result-to-widget.v{_MAJOR_VERSION}+json"
)
