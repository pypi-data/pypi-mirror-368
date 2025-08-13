from collections.abc import Mapping
from typing import Protocol


class Authenticate(Protocol):
    """Called with the URL of a request and return the HTTP headers necessary to authenticate it.

    There are some built-in implementations:

    * :class:`atoti.BasicAuthentication`
    * :class:`atoti.OAuth2ResourceOwnerPasswordAuthentication`
    * :class:`atoti.TokenAuthentication`
    """

    def __call__(self, url: str, /) -> Mapping[str, str]: ...
