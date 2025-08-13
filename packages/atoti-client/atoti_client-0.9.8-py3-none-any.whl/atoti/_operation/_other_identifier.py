from typing import TypeVar

from .._identification import Identifier

OtherIdentifierT_co = TypeVar("OtherIdentifierT_co", bound=Identifier, covariant=True)
