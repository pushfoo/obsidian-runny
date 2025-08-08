"""Annotation types used throughout the project.

**IMPORTANT:** MUST NOT contain obsidian_runny imports!

This module must be usable at any time without circular imports.
"""
from collections.abc import Iterable, Mapping
from typing_extensions import (
    Callable,
    Generic,
    Hashable,
    ParamSpec,
    Protocol,
    TypeVar
)

__all__ = [
    'PairFormatter',
    'ParamsFormatter',
    'DictArgsLike',
    'P',
    'K',
    'V',
    'V_co',
    'R',
    'R_co'
]

P = ParamSpec("P")

K = TypeVar("K", bound=Hashable)
"""Keys in containers."""


V = TypeVar("V")
"""Values in containers."""


R = TypeVar("R")
"""Return types."""


# Covariant versions of above type variables
V_co = TypeVar("V_co", covariant=True)
R_co = TypeVar("R_co", covariant=True)


DictArgsLike = Mapping[K, V] | Iterable[tuple[K, V]]
PairFormatter = Callable[P, R_co]


class ParamsFormatter(Protocol, Generic[P, R_co]):

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> R_co:
        raise NotImplementedError("Abstract")


KEY_TUPLE = tuple[str, ...]
