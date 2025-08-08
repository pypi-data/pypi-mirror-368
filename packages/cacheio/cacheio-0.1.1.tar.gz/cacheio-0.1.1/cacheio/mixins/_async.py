from __future__ import annotations

from abc import ABC

from cacheio import CacheFactory


class AsyncCacheable(ABC):
    def __init__(self, *args, **kwargs):
        self._cache = CacheFactory.async_memory_cache()
        super().__init__(*args, **kwargs)


__all__ = ("AsyncCacheable",)
