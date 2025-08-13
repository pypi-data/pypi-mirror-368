from typing import Annotated, TypeAlias

from pydantic import AfterValidator

from .has_identifier import HasIdentifier, IdentifierT_co

_Identifiable: TypeAlias = HasIdentifier[IdentifierT_co] | IdentifierT_co


def identify(identifiable: _Identifiable[IdentifierT_co], /) -> IdentifierT_co:
    return (
        identifiable._identifier
        if isinstance(identifiable, HasIdentifier)
        else identifiable
    )


Identifiable = Annotated[
    _Identifiable[IdentifierT_co],
    # Normalizing to an `Identifier` to ensure runtime immutability of `Identifiable` fields on frozen dataclasses.
    # This allows such dataclasses to be hashed and used as keys in a mapping.
    AfterValidator(identify),
]
