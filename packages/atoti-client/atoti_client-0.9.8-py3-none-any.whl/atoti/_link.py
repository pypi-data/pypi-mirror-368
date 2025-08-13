from __future__ import annotations

from dataclasses import dataclass, replace
from typing import final

from typing_extensions import override

from ._mime_type import LINK_MIME_TYPE, TEXT_MIME_TYPE


@final
@dataclass(frozen=True, kw_only=True)
class Link:
    session_url: str
    path: str = ""

    @property
    def _url(self) -> str:
        url = self.session_url

        if self.path:
            url += f"/{self.path}"

        return url

    @override
    def __repr__(self) -> str:
        text = self._repr_mimebundle_({}, {})[TEXT_MIME_TYPE]
        assert isinstance(text, str)
        return text

    def __truediv__(self, path: str, /) -> Link:
        assert path
        return replace(self, path=f"{self.path}/{path}" if self.path else path)

    def _repr_mimebundle_(
        self,
        include: object,  # noqa: ARG002
        exclude: object,  # noqa: ARG002
    ) -> dict[str, object]:
        return {
            LINK_MIME_TYPE: {
                "path": self.path,
                "sessionUrl": self.session_url,
            },
            TEXT_MIME_TYPE: self._url,
        }
