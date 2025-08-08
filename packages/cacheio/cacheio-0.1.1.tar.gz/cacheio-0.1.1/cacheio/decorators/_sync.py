from __future__ import annotations

import functools
from typing import Callable, Concatenate, ParamSpec, TypeVar, TYPE_CHECKING

from cacheio._types import T, R, SyncMethod, SyncDecorator
from cacheio._utils import ensure_decorated_class_method, ensure_cache_adapter

if TYPE_CHECKING:
    from cachelib import BaseCache
    from cacheio.protocols import AdapterProtocol

    TBackend = TypeVar("TBackend", bound=BaseCache)

P = ParamSpec("P")


def cached(
    *,
    cache_attr: str = "_cache",
    ttl: int | None = None,
) -> SyncDecorator[T, P, R]:
    """
    A decorator for caching a synchronous function's result using a synchronous cache
    adapter.

    The decorator generates a cache key internally and delegates caching logic to a
    synchronous cache adapter found on the decorated object.

    :param cache_attr: The name of the attribute on ``self`` that holds the cache
                       adapter.
    :type cache_attr: str
    :param ttl: The time-to-live for the cached item in seconds.
    :type ttl: int | None
    :return: The decorated async function (wrapper).
    :rtype: SyncMethod[T, P, R | None]
    """

    def decorator(
        fn: SyncMethod[T, P, R],
    ) -> SyncMethod[T, P, R | None]:
        ensure_decorated_class_method(fn, "cached")

        @functools.wraps(fn)
        def wrapper(
            self: T,
            *args: P.args,
            **kwargs: P.kwargs,
        ) -> R | None:
            """
            The wrapper function that executes the caching logic before
            calling the original decorated function.
            """
            ensure_cache_adapter(self, cache_attr)
            adapter: AdapterProtocol = getattr(self, cache_attr)

            return adapter.get_or_set(
                f"{fn.__module__}.{fn.__qualname__}",
                lambda: fn(self, *args, **kwargs),
                ttl=ttl,
            )

        return wrapper

    return decorator


def memoized(
    key_fn: Callable[Concatenate[T, P], str],
    *,
    cache_attr: str = "_cache",
    ttl: int | None = None,
) -> SyncDecorator[T, P, R]:
    """
    A decorator for caching a synchronous function's result using a synchronous cache
    adapter.

    The decorator generates a cache key using ``key_fn`` and delegates caching logic to
    a synchronous cache adapter found on the decorated object.

    :param key_fn: A function that generates a cache key from the decorated
                   function's arguments.
    :type key_fn: KeyCallable[P]
    :param cache_attr: The name of the attribute on ``self`` that holds the cache
                       adapter.
    :type cache_attr: str
    :param ttl: The time-to-live for the cached item in seconds.
    :type ttl: int | None
    :return: The decorated function (wrapper).
    :rtype: SyncMethod[T, P, R | None]
    """

    def decorator(
        fn: SyncMethod[T, P, R],
    ) -> SyncMethod[T, P, R | None]:
        ensure_decorated_class_method(fn, "memoized")

        @functools.wraps(fn)
        def wrapper(
            self: T,
            *args: P.args,
            **kwargs: P.kwargs,
        ) -> R | None:
            """
            The wrapper function that executes the caching logic before
            calling the original decorated function.
            """
            ensure_cache_adapter(self, cache_attr)
            adapter: AdapterProtocol = getattr(self, cache_attr)

            return adapter.get_or_set(
                key_fn(self, *args, **kwargs),
                lambda: fn(self, *args, **kwargs),
                ttl=ttl,
            )

        return wrapper

    return decorator


__all__ = (
    "cached",
    "memoized",
)
