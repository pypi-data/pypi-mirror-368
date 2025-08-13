"""This subpackage is named in plural to be consistent with Python's built-in `collections` subpackage."""

from .delegating_converting_mapping import (
    DelegatingConvertingMapping as DelegatingConvertingMapping,
)
from .delegating_key_disambiguating_mapping import (
    DelegatingKeyDisambiguatingMapping as DelegatingKeyDisambiguatingMapping,
)
from .delegating_mutable_mapping import (
    DelegatingMutableMapping as DelegatingMutableMapping,
)
from .delegating_mutable_set import DelegatingMutableSet as DelegatingMutableSet
from .frozen_collections import (
    FrozenMapping as FrozenMapping,
    FrozenSequence as FrozenSequence,
)
from .frozendict import frozendict as frozendict
from .supports_unchecked_mapping_lookup import (
    SupportsUncheckedMappingLookup as SupportsUncheckedMappingLookup,
)
