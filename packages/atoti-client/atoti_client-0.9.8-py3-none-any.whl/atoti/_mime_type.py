from importlib.metadata import version

HTML_MIME_TYPE = "text/html"
MARKDOWN_MIME_TYPE = "text/markdown"
PNG_MIME_TYPE = "image/png"
TEXT_MIME_TYPE = "text/plain"

_MAJOR_VERSION = version("atoti-client").split(".", maxsplit=1)[0]

LINK_MIME_TYPE = f"application/vnd.atoti.link.v{_MAJOR_VERSION}+json"
WIDGET_MIME_TYPE = f"application/vnd.atoti.widget.v{_MAJOR_VERSION}+json"
