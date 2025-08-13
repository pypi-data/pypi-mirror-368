from collections.abc import Set as AbstractSet
from contextvars import ContextVar

CONTEXT_VAR: ContextVar[AbstractSet[str]] = ContextVar(
    "atoti_allowed_experimental_feature_keys", default=frozenset()
)
