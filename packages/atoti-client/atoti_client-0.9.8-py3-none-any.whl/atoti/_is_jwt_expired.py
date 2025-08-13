from base64 import urlsafe_b64decode
from datetime import timedelta
from time import time

from ._pydantic import get_type_adapter


def _parse_jwt_claims(jwt: str, /) -> dict[str, object]:
    _header, encoded_payload, _signature = jwt.split(".")
    # Pad base64 if necessary
    padding = "=" * (-len(encoded_payload) % 4)
    encoded_payload += padding
    payload = urlsafe_b64decode(encoded_payload)
    type_adapter = get_type_adapter(dict[str, object])
    return type_adapter.validate_json(payload)


_DEFAULT_MARGIN = timedelta(minutes=30)


def is_jwt_expired(jwt: str, /, *, margin: timedelta = _DEFAULT_MARGIN) -> bool:
    claims = _parse_jwt_claims(jwt)

    expiry = claims.get("exp")

    if expiry is None:
        return False

    assert isinstance(expiry, int | str)

    now = time()
    return (now + margin.total_seconds()) > int(expiry)
