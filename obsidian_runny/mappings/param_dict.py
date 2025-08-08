"""Helper containers and related functions."""
from collections.abc import Iterable, Mapping, Sequence
import inspect
from typing import Generator
from obsidian_runny.annotations import K, V, DictArgsLike

from typing_extensions import Self

from obsidian_runny.mappings.iteration import iter_as_pairs
from obsidian_runny.mappings.iteration.keygrabs import get_keys


__all__ = [
    "ParamDict"
]

def _as_dict_args(
        args: Sequence[DictArgsLike[str, V]],
        kwargs: DictArgsLike[str, V]
) -> Generator[tuple[str, V], None, None]:
        print("eee", args, kwargs)
        copy_from: DictArgsLike[str, V] = ()
        if not isinstance(kwargs, Mapping):
            kwargs = dict(kwargs)
        match bool(len(args)), bool(len(kwargs)):
            case True, True:
                raise TypeError("Expects only 1 arg or kwarg values")
            case False, True:
                copy_from = kwargs
            case True, False:
                copy_from = args[0] # type: ignore
            case _, _:
                pass
        yield from iter_as_pairs(copy_from)


class ParamDict(dict[str, V]):
    """Deletes keys which would be set to `None` values.

    This is because Obsidian's built-in URI scheme does
    not have any `None` or null values. Therefore, this
    class:

    1. At creation, skip all `(k, v)` where `v == None`
    2. Setting an instance's key to `None` deletes it
    """

    def __init__(
        self,
        *args: DictArgsLike[str, V],
        **kwargs: V
    ):
        super().__init__()
        self._update_core(args, kwargs)

    def _update_core(
            self,
            args: Sequence[DictArgsLike[str, V]] = (),
            kwargs: DictArgsLike[str, V] = ()
    ) -> None:
        """Avoid unpack/repack."""
        for k, v in _as_dict_args(args, kwargs):
            if v is None:
                continue
            self[k] = v

    def update(self, *args, **kwargs) -> None:
        self._update_core(args, kwargs)

    def __setitem__(self, k: str, v: V | None) -> None:
        if v is not None:
            super().__setitem__(k, v) # type: ignore
        elif k in self:
            del self[k]

    @classmethod
    def as_instance(cls, other) -> Self:
        if isinstance(other, cls):
            return other
        try:
            iter(other)
        except TypeError as e:
            raise TypeError(f"Cannot convert non-iterable to type {cls.__name__}")

        return cls(other)
