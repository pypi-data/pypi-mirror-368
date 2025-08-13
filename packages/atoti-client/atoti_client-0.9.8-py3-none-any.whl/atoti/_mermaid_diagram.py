import os
from abc import ABC, abstractmethod
from base64 import b64encode, urlsafe_b64encode
from typing import final

import httpx
from typing_extensions import override

from ._env import get_env_flag
from ._mime_type import (
    HTML_MIME_TYPE as _HTML_MIME_TYPE,
    MARKDOWN_MIME_TYPE as _MARKDOWN_MIME_TYPE,
    PNG_MIME_TYPE as _PNG_MIME_TYPE,
)

_MERMAID_HTML_REPR_ENV_VAR_NAME = "_ATOTI_MERMAID_HTML_REPR"
"""Set this environment variable to true to replace Markdown with HTML in the mime bundle of diagrams."""

_MERMAID_INK_URL_ENV_VAR_NAME = "_ATOTI_MERMAID_INK_URL"
"""Set this environment variable to the URL of a https://github.com/jihchi/mermaid.ink deployment (e.g. https://mermaid.ink) to render diagrams to PNG and use that in the mime bundle instead of Markdown.

This is useful for notebook previewing environments that do not support rendering Mermaid diagrams in cell outputs such as GitHub.

Do not pass the URL of a public service if diagrams are meant to stay private.
"""


class MermaidDiagram(ABC):
    @property
    @abstractmethod
    def _mermaid_diagram_code(self) -> str: ...

    @override
    def __repr__(self) -> str:
        return self._mermaid_diagram_code

    @final
    def _repr_mimebundle_(
        self,
        include: object,  # noqa: ARG002
        exclude: object,  # noqa: ARG002
    ) -> dict[str, str]:
        diagram_code = self._mermaid_diagram_code

        # Another design would be to detect whether https://github.com/mermaid-js/mermaid-cli is installed locally and use that to automatically convert diagram codes to images.
        # This CLI is heavy since it pulls a browser required to render diagrams.
        # It is more portable to run https://github.com/jihchi/mermaid.ink/blob/main/Dockerfile locally and set this environment variable to the corresponding localhost URL.
        mermaid_ink_url = os.environ.get(_MERMAID_INK_URL_ENV_VAR_NAME)

        if mermaid_ink_url:
            encoded_diagram = urlsafe_b64encode(diagram_code.encode()).decode()
            # Even though mermaid.ink supports SVG, PNG is used because:
            # - Generated SVG files contain `<style />` tags that GitHub would strip away during sanitation, breaking the rendering of the diagram.
            # - When setting the generated SVG as the `src` of an `<img />` with the HTML mime type, the `style` attribute declaring its `max-width` would be ignored, leading the image to take all the available width, and thus the diagram would often look way too big.
            url = f"{mermaid_ink_url.rstrip('/')}/img/{encoded_diagram}?type=png"
            # Another design would be to `return {_HTML_MIME_TYPE: f"<img src='{url}'>"}`, postponing the HTTP request to the moment users view the notebook in their browser, and keeping the notebook lighter (the URL takes less bytes than the encoded diagram).
            # The drawback of this alternative design is that if the URL is down when users view the notebook, the image would not display.
            # Embedding the image is future proof.
            response = httpx.get(
                url,
                headers={
                    "accept": _PNG_MIME_TYPE,
                    "user-agent": "atoti",  # Without a user agent, the server answers with a 403.
                },
            ).raise_for_status()
            png = response.content
            encoded_png = b64encode(png).decode()
            return {_PNG_MIME_TYPE: encoded_png}

        if get_env_flag(_MERMAID_HTML_REPR_ENV_VAR_NAME):
            return {_HTML_MIME_TYPE: f"""<div class="mermaid">{diagram_code}</div>"""}

        return {_MARKDOWN_MIME_TYPE: f"```mermaid\n{diagram_code}```\n"}
