"""Annotation types used throughout the project.

**IMPORTANT:** MUST NOT contain obsidian_runny imports!

This module must be usable at any time without circular imports.
"""
from typing_extensions import (
    Any,
    Callable,
    Generic,
    Mapping,
    ParamSpec,
    Protocol,
    TypeVar
)

__all__ = [
    'PairFormatter',
    'ParamsFormatter',
    'P',
    'V',
    'V_co',
    'R',
    'R_co'
]

P = ParamSpec("P")
V = TypeVar("V")
V_co = TypeVar("V_co", covariant=True)
R = TypeVar("R")
R_co = TypeVar("R_co", covariant=True)

PairFormatter = Callable[P, R_co]


class ParamsFormatter(Protocol, Generic[P, R_co]):

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> R_co:
        raise NotImplementedError("Abstract")

