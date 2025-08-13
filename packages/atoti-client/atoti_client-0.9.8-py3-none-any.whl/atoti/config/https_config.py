from typing import Annotated, final

from pydantic import Field, FilePath
from pydantic.dataclasses import dataclass

from .._pydantic import PYDANTIC_CONFIG as _PYDANTIC_CONFIG


@final
@dataclass(config=_PYDANTIC_CONFIG, frozen=True, kw_only=True)
class HttpsConfig:
    """The PKCS 12 keystore config to enable HTTPS on the application.

    Note:
        PEM or DER certificates can be `converted to PKCS 12 with OpenSSL <https://stackoverflow.com/questions/56241667/convert-certificate-in-der-or-pem-to-pkcs12/56244685#56244685>`__.

    """

    certificate: FilePath
    """The path to the certificate."""

    password: str
    """The password to read the certificate."""

    domain: Annotated[str, Field(exclude=True)] = "localhost"
    """The domain certified by the certificate."""

    certificate_authority: Annotated[FilePath | None, Field(exclude=True)] = None
    """Path to the custom certificate authority to use to verify the HTTPS connection.

    Required when *certificate* is not signed by some trusted public certificate authority.
    """
