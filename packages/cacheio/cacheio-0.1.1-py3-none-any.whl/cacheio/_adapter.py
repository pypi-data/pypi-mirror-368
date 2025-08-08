from __future__ import annotations

from typing import Callable, Dict, List, ParamSpec, TypeVar, TYPE_CHECKING

from ._types import R

if TYPE_CHECKING:
    from cachelib import BaseCache

    TBackend = TypeVar("TBackend", bound=BaseCache)

P = ParamSpec("P")


class Adapter:
    """
    A concrete cache adapter for synchronous caching backends, such as `cachelib`.

    This adapter provides a high-level, synchronous interface for common caching
    operations, allowing for memoization and data retrieval using an underlying
    synchronous cache backend.
    """

    __slots__ = ("_backend",)

    def __init__(
        self,
        backend: TBackend,
    ) -> None:
        self._backend = backend

    def has(
        self,
        key: str,
    ) -> bool:
        """
        Checks for the existence of a key in the cache.

        This method is an efficient, atomic way to determine if a key exists
        without retrieving its value.

        :param key: The key associated with the value.
        :type key: str
        :return: ``True`` if the key exists, ``False`` otherwise.
        :rtype: bool
        """
        return self._backend.has(key)

    def get(
        self,
        key: str,
    ) -> R | None:
        """
        Retrieves a value from the cache by its key.

        :param key: The key associated with the value.
        :type key: str
        :return: The cached value, or ``None`` if the key is not found.
        :rtype: R | None
        """
        return self._backend.get(key)

    def get_many(
        self,
        *keys: str,
    ) -> List[R | None]:
        """
        Retrieve multiple values for the given keys.

        :param keys: Tuple of keys to retrieve.
        :type keys: tuple[str, ...]
        :return: List of values corresponding to keys; missing keys return ``None``.
        :rtype: List[R | None]
        """
        return self._backend.get_many(*keys)

    def multi_get(
        self,
        *keys: str,
    ) -> List[R | None]:
        """
        Retrieve multiple values for the given keys.

        :param keys: Tuple of keys to retrieve.
        :type keys: tuple[str, ...]
        :return: List of values corresponding to keys; missing keys return ``None``.
        :rtype: List[R | None]
        """
        return self._backend.get_many(*keys)

    def set(
        self,
        key: str,
        value: R,
        *,
        ttl: int | None = None,
    ) -> None:
        """
        Stores a value in the cache with an optional time-to-live (TTL).

        :param key: The key to store the value under.
        :type key: str
        :param value: The value to be cached.
        :type value: Any
        :param ttl: The time-to-live for the cache entry in seconds.
        :type ttl: int | None
        """
        return self._backend.set(key, value, timeout=ttl)

    def set_many(
        self,
        mapping: Dict[str, R],
        *,
        ttl: int | None = None,
    ) -> None:
        """
        Stores multiple key-value pairs with an optional TTL.

        :param mapping: Dictionary of keys and values to set.
        :type mapping: Dict[str, Any]
        :param ttl: The time-to-live for the cache entries in seconds.
        :type ttl: int | None
        """
        self._backend.set_many(mapping, timeout=ttl)

    def multi_set(
        self,
        mapping: Dict[str, R],
        *,
        ttl: int | None = None,
    ) -> None:
        """
        Stores multiple key-value pairs with an optional TTL.

        :param mapping: Dictionary of keys and values to set.
        :type mapping: Dict[str, Any]
        :param ttl: The time-to-live for the cache entries in seconds.
        :type ttl: int | None
        """
        self._backend.set_many(mapping, timeout=ttl)

    def add(
        self,
        key: str,
        value: R,
        *,
        ttl: int | None = None,
    ) -> bool:
        """
        Stores the value in the given key with TTL if specified.
        Raises an error if the key already exists.

        :param key: The key to store the value under.
        :type key: str
        :param value: The value to be cached.
        :type value: Any
        :param ttl: The time-to-live for the cache entry in seconds.
            Due to memcached restrictions, use int for compatibility.
            Redis and memory caches support float TTLs.
        :type ttl: int | None
        :return: True if the key was successfully inserted.
        :rtype: bool
        """
        return self._backend.add(key, value, timeout=ttl)

    def get_or_set(
        self,
        key: str,
        fn: Callable[[], R],
        *,
        ttl: int | None = None,
    ) -> R | None:
        """
        Executes a synchronous callable and caches its result.

        If the key exists in the cache, the cached value is returned. Otherwise,
        the callable ``fn`` is executed, its result is cached, and then returned.

        :param key: The cache key for the result of the callable.
        :type key: str
        :param fn: The callable to execute if the key is not in the cache.
                   It must be a no-argument callable that returns a value of type R.
        :type fn: Callable[[], R]
        :param ttl: The time-to-live for the cache entry in seconds.
        :type ttl: int | None
        :return: The result of the callable or the cached value.
        :rtype: R | None
        """
        if self._backend.has(key):
            return self._backend.get(key)

        value = fn()
        self._backend.set(key, value, timeout=ttl)

        return value

    def delete(
        self,
        key: str,
    ) -> bool:
        """
        Deletes a key from the cache.

        :param key: The key to delete.
        :type key: str
        """
        return self._backend.delete(key)

    def delete_many(
        self,
        *keys: str,
    ) -> None:
        """
        Deletes multiple keys from the cache.

        :param keys: Tuple of keys to delete.
        :type keys: tuple[str, ...]
        """
        self._backend.delete_many(*keys)

    def multi_delete(
        self,
        *keys: str,
    ) -> None:
        """
        Deletes multiple keys from the cache.

        :param keys: Tuple of keys to delete.
        :type keys: tuple[str, ...]
        """
        self._backend.delete_many(*keys)

    def increment(
        self,
        key: str,
        amount: int = 1,
    ) -> int | None:
        """
        Increments the integer value stored at the given key by the specified amount.

        If the key does not exist, it is initialized to 0 before incrementing.

        :param key: The key whose value to increment.
        :type key: str
        :param amount: The amount to increment by (default is 1).
        :type amount: int
        :return: The new value after incrementing.
        :rtype: int | None
        """
        return self._backend.inc(key, amount)

    def decrement(
        self,
        key: str,
        amount: int = 1,
    ) -> int | None:
        """
        Decrements the integer value stored at the given key by the specified amount.

        If the key does not exist, it is initialized to 0 before decrementing.

        :param key: The key whose value to decrement.
        :type key: str
        :param amount: The amount to decrement by (default is 1).
        :type amount: int
        :return: The new value after decrementing.
        :rtype: int | None
        """
        return self._backend.dec(key, amount)

    def clear(
        self,
    ) -> bool:
        """
        Clears all items from the cache.

        :return: ``True`` if the cache was successfully cleared, ``False`` otherwise.
        :rtype: bool
        """
        return self._backend.clear()


__all__ = ("Adapter",)
