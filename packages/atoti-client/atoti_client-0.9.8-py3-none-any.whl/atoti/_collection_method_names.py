from collections.abc import Collection

COLLECTION_METHOD_NAMES: Collection[str] = {
    "__delitem__",
    "__getitem__",
    "__iadd__",
    "__setitem__",
    "add",
    "discard",
    "update",
}
"""Names of methods operating on a collection and accepting some arguments (i.e. call validation is useful)."""
