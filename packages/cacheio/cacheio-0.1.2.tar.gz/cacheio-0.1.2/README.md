# cacheio
![Python Version](https://img.shields.io/badge/python-3.10%2B-blue) ![License](https://img.shields.io/github/license/bnlucas/cacheio) ![PyPI - Version](https://img.shields.io/pypi/v/cacheio)

A flexible and user-friendly Python caching utility that provides a **unified interface** for both synchronous and asynchronous caching, **wrapping and integrating** two well-established caching libraries: [`cachelib`](https://github.com/pallets/cachelib) for synchronous caching, and [`aiocache`](https://github.com/aio-libs/aiocache) for asynchronous caching.

`cacheio` simplifies caching in Python applications by providing a consistent API for both sync and async use cases — no need to learn two different interfaces or manage separate dependencies manually. It intelligently loads only the backend dependencies you need.

---

## Overview 🚀

`cacheio` offers a unified caching interface for Python developers, abstracting away the differences between synchronous and asynchronous caching libraries. By wrapping [`cachelib`](https://github.com/pallets/cachelib) for sync caching and [`aiocache`](https://github.com/aio-libs/aiocache) for async caching, it lets you write caching logic that is clean, consistent, and easy to maintain.

---

## Installation

You can install `cacheio` via pip. It supports optional dependency groups for backend support.

### Basic Installation

Install core library without caching backends:

```bash
pip install cacheio
```

### Installing with Backends

- **Synchronous caching (cachelib-based):**

```bash
pip install "cacheio[sync]"
```

- **Asynchronous caching (aiocache-based):**

```bash
pip install "cacheio[async]"
```

- **Full installation (both sync and async):**

```bash
pip install "cacheio[full]"
```

---

## Quick Start

### Synchronous Caching

Use `CacheFactory.memory_cache()` to get a sync cache adapter backed by `cachelib`.

```python
from cacheio import CacheFactory

cache = CacheFactory.memory_cache()

cache.set("my_key", "my_value", ttl=300)
print(cache.get("my_key"))
```

### Asynchronous Caching

Use `CacheFactory.async_memory_cache()` to get an async cache adapter backed by `aiocache`.

```python
import asyncio
from cacheio import CacheFactory

async def main():
    async_cache = CacheFactory.async_memory_cache()
    await async_cache.set("my_async_key", "my_async_value", ttl=300)
    val = await async_cache.get("my_async_key")
    print(val)

asyncio.run(main())
```

---

## Using Decorators for Method Result Caching

`cacheio` provides four decorators to easily cache method results with minimal boilerplate:

- `@cached`: Sync decorator with automatic cache key generation.
- `@memoized`: Sync decorator with user-defined key function.
- `@async_cached`: Async decorator with automatic cache key generation.
- `@async_memoized`: Async decorator with user-defined async key function.

### 1. Synchronous `@cached`

Automatically caches method results using method arguments as the cache key.

```python
from cacheio import cached
from cacheio.mixins import Cacheable

class UserService(Cacheable):
    @cached(ttl=60)
    def fetch_user(self, user_id: int) -> dict:
        print(f"Fetching user {user_id} from DB...")
        return {"id": user_id, "name": f"User_{user_id}"}

service = UserService()
print(service.fetch_user(1))  # Runs and caches
print(service.fetch_user(1))  # Returns cached result
```

### 2. Synchronous `@memoized`

Allows a custom cache key function for more control.

```python
from cacheio import memoized
from cacheio.mixins import Cacheable

class UserService(Cacheable):
    @memoized(key_fn=lambda self, user_id, **kwargs: f"user:{user_id}", ttl=60)
    def fetch_user(self, user_id: int, request_id: str) -> dict:
        print(f"Fetching user {user_id} with request {request_id}")
        return {"id": user_id, "request": request_id}

service = UserService()
print(service.fetch_user(1, request_id="abc"))  # Cached by user_id only
print(service.fetch_user(1, request_id="xyz"))  # Returns cached result (same key)
```

### 3. Asynchronous `@async_cached`

Async version of `@cached`, for async methods.

```python
import asyncio
from cacheio import async_cached
from cacheio.mixins import AsyncCacheable

class AsyncUserService(AsyncCacheable):
    @async_cached(ttl=60)
    async def fetch_user(self, user_id: int) -> dict:
        print(f"Fetching user {user_id} asynchronously...")
        await asyncio.sleep(2)
        return {"id": user_id, "name": f"User_{user_id}"}

async def main():
    service = AsyncUserService()
    print(await service.fetch_user(1))  # Runs and caches
    print(await service.fetch_user(1))  # Returns cached result

asyncio.run(main())
```

### 4. Asynchronous `@async_memoized`

Async decorator with a custom async key function.

```python
import asyncio
from cacheio import async_memoized
from cacheio.mixins import AsyncCacheable

class AsyncUserService(AsyncCacheable):
    @async_memoized(key_fn=lambda self, user_id, **kwargs: f"user:{user_id}", ttl=60)
    async def fetch_user(self, user_id: int, request_id: str) -> dict:
        print(f"Fetching user {user_id} with request {request_id} asynchronously...")
        await asyncio.sleep(2)
        return {"id": user_id, "request": request_id}

async def main():
    service = AsyncUserService()
    print(await service.fetch_user(1, request_id="abc"))  # Cached
    print(await service.fetch_user(1, request_id="xyz"))  # Returns cached result

asyncio.run(main())
```

---

## Configuration

You can customize global caching behavior via the `config` object and the `configure()` function.

Example:

```python
from cacheio import config, configure

def update_settings(cfg):
    cfg.default_ttl = 600
    cfg.default_threshold = 1000

configure(update_settings)
```

This allows centralized control of defaults like TTL and cache size threshold.

---

## Contributing

Contributions are welcome! Feel free to open issues or submit pull requests on our [GitHub repository](https://github.com/bnlucas/cacheio).

---

## License

`cacheio` is distributed under the MIT license. See the [LICENSE](https://github.com/bnlucas/cacheio/blob/main/LICENSE) file for details.
