"""Helper data structures.

These will mostly be filtering / key behavior an object.
"""
from obsidian_runny.annotations import V
from collections.abc import Iterable, Mapping

__all__ = [
    "ParamDict"
]

class ParamDict(dict[str, V]):
    """Filters / deletes ``None`` keys."""

    def __init__(self, *args, **kwargs):
        super().__init__()
        copy_from = None

        match (len(args), bool(len(kwargs))):
            case 0, _:
                copy_from = kwargs.items()
            case 1, True:
                raise TypeError("Can't set from args and kwargs")
            case 1, False:
                first = args[0] # type: ignore
                if not isinstance(first, Iterable):
                    raise TypeError(
                        "Positional argument must be mapping of iterable of pairs")
                elif isinstance(first, Mapping):
                    copy_from = first.items()
                else:
                    copy_from = first

            case _, _:
                raise TypeError("Expects only 1 arg or kwarg values")

        for k, v in copy_from: # type: ignore
            if v is None:
                continue
            self[k] = v

    def __setitem__(self, k: str, v: V | None):
        if v is None and k in self:
            del self[k]
        else:
            super().__setitem__(k, v) # type: ignore

