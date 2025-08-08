from __future__ import annotations

from typing import Any

try:
    from cachelib import SimpleCache as Cache
except ImportError:
    Cache = None

try:
    from aiocache import Cache as AsyncCache
except ImportError:
    AsyncCache = None

from ._config import config
from ._async_adapter import AsyncAdapter
from ._adapter import Adapter


class CacheFactory:
    """
    A factory class for building synchronous and asynchronous cache adapters.
    """

    @staticmethod
    def memory_cache(
        *,
        ttl: int | None = None,
        threshold: int = 500,
    ) -> Adapter:
        """
        Builds a synchronous `CacheAdapter` instance using an in-memory backend.

        This method creates a `cachelib.SimpleCache` with the specified
        parameters and wraps it in a `CacheAdapter`. The TTL defaults
        to a value from the `config.default_ttl`.

        :param ttl: The time-to-live for cache entries in seconds.
        :type ttl: int | None
        :param threshold: The maximum number of items the cache stores before it
                          starts deleting some.
        :type threshold: int
        :return: A configured `CacheAdapter` instance.
        :rtype: CacheAdapter
        """
        if Cache is None:
            raise ImportError(
                "The 'cachelib' library is not installed. Please install "
                "'cacheio[sync]' to use synchronous caching."
            )

        ttl = int(ttl or config.default_ttl)
        threshold = int(threshold or config.default_threshold)

        return Adapter(Cache(threshold, ttl))

    @staticmethod
    def async_memory_cache(
        *,
        ttl: int | None = None,
        **kwargs: Any,
    ) -> AsyncAdapter:
        """
        Builds an asynchronous `AsyncCacheAdapter` instance using an in-memory backend.

        This method creates an `aiocache.Cache` instance with an in-memory
        backend and wraps it in an `AsyncCacheAdapter`. The TTL defaults
        to a value from the `config.default_ttl`.

        :param ttl: The time-to-live for cache entries in seconds.
        :type ttl: int | None
        :param kwargs: Additional keyword arguments to pass to the cache constructor.
        :type kwargs: Any
        :return: A configured `AsyncCacheAdapter` instance.
        :rtype: AsyncCacheAdapter
        """
        if AsyncCache is None:
            raise ImportError(
                "The 'aiocache' library is not installed. Please install "
                "'cacheio[async]' to use asynchronous caching."
            )

        ttl = int(ttl or config.default_ttl)
        return AsyncAdapter(AsyncCache(AsyncCache.MEMORY, ttl=ttl, **kwargs))


__all__ = ("CacheFactory",)
