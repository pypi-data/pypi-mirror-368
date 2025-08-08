from __future__ import annotations

from typing import (
    Awaitable,
    Callable,
    Concatenate,
    ParamSpec,
    TypeVar,
)

TBackend = TypeVar("TBackend")

P = ParamSpec("P")
T = TypeVar("T")
R = TypeVar("R")

SyncMethod = Callable[Concatenate[T, P], R | None]
AsyncMethod = Callable[Concatenate[T, P], Awaitable[R | None]]

SyncDecorator = Callable[[SyncMethod[T, P, R]], SyncMethod[T, P, R | None]]
AsyncDecorator = Callable[[AsyncMethod[T, P, R]], AsyncMethod[T, P, R | None]]


__all__ = (
    "TBackend",
    "T",
    "R",
    "SyncMethod",
    "SyncDecorator",
    "AsyncMethod",
    "AsyncDecorator",
)
