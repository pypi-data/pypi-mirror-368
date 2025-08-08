from __future__ import annotations

from typing import (
    Awaitable,
    Callable,
    Dict,
    List,
    Protocol,
    TYPE_CHECKING,
)

if TYPE_CHECKING:
    from cacheio._types import R


class AsyncAdapterProtocol(Protocol):
    """
    Protocol for asynchronous cache adapters.

    Provides a uniform interface for asynchronous caching backends,
    including methods for getting, setting, deleting keys, batch operations,
    and increment/decrement support.
    """

    async def has(
        self,
        key: str,
    ) -> Awaitable[bool]:
        """
        Checks for the existence of a key in the cache.

        This method is an efficient, atomic way to determine if a key exists
        without retrieving its value.

        :param key: The key associated with the value.
        :type key: str
        :return: ``True`` if the key exists, ``False`` otherwise.
        :rtype: Awaitable[bool]
        """
        ...

    async def get(
        self,
        key: str,
    ) -> Awaitable[R | None]:
        """
        Retrieves a value from the cache by its key.

        :param key: The key associated with the value.
        :type key: str
        :return: The cached value, or ``None`` if the key is not found.
        :rtype: Awaitable[R | None]
        """
        ...

    async def get_many(
        self,
        *keys: str,
    ) -> Awaitable[List[R | None]]:
        """
        Retrieve multiple values for the given keys.

        :param keys: Tuple of keys to retrieve.
        :type keys: tuple[str, ...]
        :return: List of values corresponding to keys; missing keys return ``None``.
        :rtype: Awaitable[List[R | None]]
        """
        ...

    async def multi_get(
        self,
        *keys: str,
    ) -> Awaitable[List[R | None]]:
        """
        Retrieve multiple values for the given keys.

        :param keys: Tuple of keys to retrieve.
        :type keys: tuple[str, ...]
        :return: List of values corresponding to keys; missing keys return ``None``.
        :rtype: Awaitable[List[R | None]]
        """
        ...

    async def set(
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
        ...

    async def set_many(
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
        ...

    async def multi_set(
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
        ...

    async def add(
        self,
        key: str,
        value: R,
        *,
        ttl: int | None = None,
    ) -> Awaitable[bool]:
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
        :rtype: Awaitable[bool]
        """
        ...

    async def get_or_set(
        self,
        key: str,
        fn: Callable[[], Awaitable[R]],
        *,
        ttl: int | None = None,
    ) -> R | None:
        """
        Retrieves a value by key or computes and caches it if not present.

        :param key: The key to retrieve or set.
        :type key: str
        :param fn: No-argument callable to compute the value if missing.
        :type fn: Callable[[], Awaitable[R]]
        :param ttl: The time-to-live for the cache entry in seconds.
        :type ttl: int | None
        :return: Cached or newly computed value.
        :rtype: R | None
        """
        ...

    async def delete(
        self,
        key: str,
    ) -> Awaitable[bool]:
        """
        Deletes a key from the cache.

        :param key: The key to delete.
        :type key: str
        :rtype: Awaitable[bool]
        """
        ...

    async def delete_many(
        self,
        *keys: str,
    ) -> None:
        """
        Deletes multiple keys from the cache.

        :param keys: Tuple of keys to delete.
        :type keys: tuple[str, ...]
        """
        ...

    async def multi_delete(
        self,
        *keys: str,
    ) -> None:
        """
        Deletes multiple keys from the cache.

        :param keys: Tuple of keys to delete.
        :type keys: tuple[str, ...]
        """
        ...

    async def increment(
        self,
        key: str,
        amount: int = 1,
    ) -> Awaitable[int | None]:
        """
        Increments the integer value stored at the given key by the specified amount.

        If the key does not exist, it is initialized to 0 before incrementing.

        :param key: The key whose value to increment.
        :type key: str
        :param amount: The amount to increment by (default is 1).
        :type amount: int
        :return: The new value after incrementing.
        :rtype: Awaitable[int | None]
        """
        ...

    async def decrement(
        self,
        key: str,
        amount: int = 1,
    ) -> Awaitable[int | None]:
        """
        Decrements the integer value stored at the given key by the specified amount.

        If the key does not exist, it is initialized to 0 before decrementing.

        :param key: The key whose value to decrement.
        :type key: str
        :param amount: The amount to decrement by (default is 1).
        :type amount: int
        :return: The new value after decrementing.
        :rtype: Awaitable[int | None]
        """
        ...

    async def clear(
        self,
    ) -> Awaitable[bool]:
        """
        Clears all items from the cache.

        :return: ``True`` if the cache was successfully cleared, ``False`` otherwise.
        :rtype: Awaitable[bool]
        """
        ...


__all__ = ("AsyncAdapterProtocol",)
