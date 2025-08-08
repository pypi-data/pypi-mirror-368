"""
A global configuration object for the caching library.

This module allows users to modify default settings, such as the time-to-live
(TTL) for cached items, in a centralized manner.
"""

from __future__ import annotations

from typing import Callable


class Config:
    """A simple configuration object to store global settings for the caching library.

    :ivar default_ttl: The default time-to-live in seconds for cache
                       entries if no specific TTL is provided.
    :vartype default_ttl: int
    """

    __slots__ = (
        "default_ttl",
        "default_threshold",
    )

    def __init__(self):
        self.default_ttl = 300
        self.default_threshold = 500


config = Config()


def configure(
    fn: Callable[[Config], None],
) -> None:
    """
    Passes the global configuration object to a function for modification.

    :param fn: A function that takes a Config object as its single argument.
    :type fn: Callable[[Config], None]
    """
    if not callable(fn):
        raise TypeError("The 'fn' argument must be a callable.")

    fn(config)


__all__ = (
    "config",
    "configure",
)
