"""Pop, get, or `action` multiple `(key, value)` pairs.

Although [`operator.itemgetter`][itemgetter] may be the
better choice at times, these are more flexible.

Before prematurely optimizing the `()` tuple allocations,
please consider that:

1. `()` is nicer `EMPTY_TUPLE` in a function signature
2. We can spare the RAM since we're not on MicroPython
3. They are only allocated once at module load-time

[itemgetter]: https://docs.python.org/3/library/operator.html#operator.itemgetter
"""
import inspect

from collections.abc import Iterable, Mapping, MutableMapping
from typing import TYPE_CHECKING, Any, Callable, Generic, overload
from operator import getitem

from obsidian_runny.annotations import K, V, DictArgsLike

__all__ = [
    'MissingKeyError',
    'DuplicateKeyError',
    'pop_item',
    'per_key',
    'get_keys',
    'pop_keys',
    'get_locals'
]


class _KeyErrorPlus(KeyError, Generic[K]):
    """De-dupe + type hint logic for keys.

    1. Stores the key name for later use in messages
    2. Permits better `from exception_instance`

    For example, the `get_locals` helper needs to report
    a KeyError for a missing variable as a `NameError`.
    """

    @property
    def key(self) -> K:
        return self._key

    def __init__(self, key: K, message: str):
        super().__init__(message)
        self._key = key


class MissingKeyError(_KeyErrorPlus[K]):

    def __init__(self, key: K, message: str | None = None):
        if message is None:
            message = f"Missing entry for {key}"
        super().__init__(key, message)


class DuplicateKeyError(_KeyErrorPlus[K]):

    def __init__(self, key: K, message: str | None = None):
        if message is None:
            message = f"Repeated key {key}"
        super().__init__(key, message)


def pop_item(m: MutableMapping[K, V], k: K) -> V:
    """`MutableMapping.pop()` as a `len`-like function.

    This is a counterpart to [`operator.getitem`][getitem].

    [getitem]: https://docs.python.org/3/library/operator.html#operator.itemgetter

    Arguments
        m: A mapping of `(key, value)` pairs.
        k: A key to remove and return from `m`.

    Returns:
        The result of `m.pop(k)`.
    """
    return m.pop(k)


if TYPE_CHECKING:
    @overload
    def per_key(
        action: Callable[[MutableMapping, K], V],
        source: MutableMapping[K, V],
        *,
        required: Iterable[K] = (),
        optional: Iterable[K] = (),
        defaults: DictArgsLike[K,V] = (),
        destination: dict[K,V] | None = None
    ) -> dict[K,V]:
        ...

    @overload
    def per_key(
        action: Callable[[MutableMapping, K], V],
        source: MutableMapping[K, V],
        *,
        required: Iterable[K] = (),
        optional: Iterable[K] = (),
        defaults: DictArgsLike[K,V] = (),
        destination: MutableMapping[K,V] | None = None
    ) -> MutableMapping[K,V]:
        ...

def per_key(
    action: Callable[[MutableMapping, K], V],
    source: MutableMapping[K, V],
    *,
    required: Iterable[K] = (),
    optional: Iterable[K] = (),
    defaults: DictArgsLike[K,V] = (),
    destination: MutableMapping[K,V] | None = None
) -> MutableMapping[K, V]:
    """Call `action` on `source` and store `(key, value)` results.

    * Creates a new `dict` if no `destination` is passed
    * Pass a `destination` to write to an existing mutabl mapping

    > [!NOTE]
    > This may consume generators despite failing fast!

    Before any other steps, it raises a `KeyError` if:

    1. Any `required` keys are absent from `source`
    2. There are duplicate keys in:
       - `required`
       - `optional`
       - `defaults`

    Then it does the following:

    1. For each required key, write `action(source, key)` to
       1. call `action(source, key)`
    2. For each `optional` key:
       * Use any present value for the key as an argument to `action`
       * Otherwise, use the value in `default` instead
    3. Write the results to `destination` or a new dict

    Arguments:
        action:
            A function which returns a value when
            passed a mapping and a key.
        source:
            The map to read from.
        required:
            An iterable of required keys.
        optional:
            An iterable of keys which will simply be
            skipped if absent.
        defaults:
            A dictionary args-like iterable which can
            be read as `(key, default_value)` pairs to
            substitute when no there is no value in the
            `source` for `key`.
        destination:
            If provided, must be a mutable mapping to permit
            writing.
    Returns:
        Either `destination` or a new `dict`.
    """
    # First we validate: change *nothing* until we know we have data!
    seen = set()
    def check_key(k, require: bool = True):
        if k in seen:
            raise DuplicateKeyError(f"duplicate key: {k}")
        elif require:
            if k in source:
                seen.add(k)
            else:
                raise MissingKeyError(f"source lacks key {k}")
        return k

    to_copy_as_is = []
    for k in required:
        check_key(k)
        to_copy_as_is.append(k)

    for k in optional:
        check_key(k, require=False)
        to_copy_as_is.append(k)

    # 1. No consumable iterables -> no unpack
    # 2. Dict handles the pair validation for us
    defaults_dict = dict(defaults)
    for k in defaults_dict.keys():
        check_key(k)

    # Temp storage we discard if something fails.
    updates = {}

    # *Now* we apply changes once we know we have them.
    for k in to_copy_as_is:
        updates[k] = action(source, k)

    for k, default in defaults_dict.items():
        if k in source:
            updates[k] = action(source, k)
        else:
            updates[k] = default

    if destination is None:
        return updates
    else:
        destination.update(updates)
        return destination


if TYPE_CHECKING:
    @overload
    def get_keys(
            source: MutableMapping[K, V],
            *,
            required: Iterable[K] = (),
            optional: Iterable[K] = (),
            defaults: DictArgsLike[K,V] = (),
    ) -> dict[K, V]:
        ...

    @overload
    def get_keys(
            source: MutableMapping[K, V],
            *,
            required: Iterable[K] = (),
            optional: Iterable[K] = (),
            defaults: DictArgsLike[K,V] = (),
            destination: MutableMapping[K,V] | None = None
    ) -> dict[K, V]:
        ...


def get_keys(
        source,
        *,
        required = (),
        optional = (),
        defaults = (),
        destination = None
):
    return per_key(
       getitem,
       source=source,
       required=required,
       optional=optional,
       defaults=defaults,
       destination=destination
    )


if TYPE_CHECKING:
    @overload
    def pop_keys(
            source: MutableMapping[K, V],
            *,
            required: Iterable[K] = (),
            optional: Iterable[K] = (),
            defaults: DictArgsLike[K,V] = (),
    ) -> dict[K, V]:
        ...

    @overload
    def pop_keys(
            source: MutableMapping[K, V],
            *,
            required: Iterable[K] = (),
            optional: Iterable[K] = (),
            defaults: DictArgsLike[K,V] = (),
            destination: MutableMapping[K,V] | None = None
    ) -> dict[K, V]:
        ...


def pop_keys(
        source,
        *,
        required = (),
        optional = (),
        defaults = (),
        destination = None
):
    return per_key(
        pop_item,
        source=source,
        required=required,
        optional=optional,
        defaults=defaults,
        destination=destination)


if TYPE_CHECKING:
    @overload
    def get_locals(
            *,
            required: Iterable[K] = (),
            optional: Iterable[K] = (),
            defaults: DictArgsLike[str,V] = (),
    ) -> dict[str, V]:
        ...

    @overload
    def get_locals(
            *,
            required: Iterable[K] = (),
            optional: Iterable[K] = (),
            defaults: DictArgsLike[K,V] = (),
            destination: MutableMapping[str,V] | None = None
    ) -> dict[str, V]:
        ...


def get_locals(
    *,
    required = (),
    optional = (),
    defaults = (),
    destination = None
):
    """Copy values from the local context into a mapping. """

    outer_frame: inspect.FrameInfo =\
        inspect.currentframe().f_back  # type: ignore
    f_locals: dict[str, Any] = outer_frame.f_locals  # type: ignore

    try:
        return get_keys(
            source=f_locals,
            required=required,
            optional=optional,
            defaults=defaults,
            destination=destination
        )
    except MissingKeyError as e:
        raise NameError(e.key) from e
