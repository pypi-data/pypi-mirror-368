from __future__ import annotations

from abc import ABC

from cacheio import CacheFactory


class Cacheable(ABC):
    def __init__(self, *args, **kwargs):
        self._cache = CacheFactory.memory_cache()
        super().__init__(*args, **kwargs)


__all__ = ("Cacheable",)
