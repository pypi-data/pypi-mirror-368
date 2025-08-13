from collections.abc import Mapping

from ..authentication import Authenticate


def get_authentication_headers(
    url: str, /, *, authenticate: Authenticate | None
) -> Mapping[str, str]:
    return {} if authenticate is None else authenticate(url)
