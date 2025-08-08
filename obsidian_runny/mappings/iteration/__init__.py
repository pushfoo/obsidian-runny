from collections.abc import Mapping
from typing import Generator
from obsidian_runny.annotations import DictArgsLike, K, V
from .keygrabs import (
    per_key,
    pop_item,
    get_keys,
    pop_keys,
    get_locals,
    MissingKeyError,
    DuplicateKeyError
)

__all__ = [
    'iter_as_pairs',
    'pop_item',
    'per_key',
    'get_keys',
    'pop_keys',
    'get_locals',
    'MissingKeyError',
    'DuplicateKeyError'
]

def iter_as_pairs(iterable: DictArgsLike[K, V]) -> Generator[tuple[K, V], None, None]:
    """Put arbitrary containers in, yield pairs.

    For a `Mapping`, it will call `.items()`. For other iterables,
    it will attempt to:

    1. Unpack to two items
    2. Yield them as `(k, v)`

    Arguments:
        iterable:
            The iterable to yield pairs from.
    """
    if isinstance(iterable, Mapping):
        yield from iterable.items()  # type: ignore
    else:
        for pair in iterable:
            k, v = pair
            yield k, v  # type: ignore