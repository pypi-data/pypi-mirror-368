# cacheio

![Python Version](https://img.shields.io/badge/python-3.10%2B-blue) ![License](https://img.shields.io/github/license/bnlucas/cacheio) ![PyPI - Version](https://img.shields.io/pypi/v/cacheio)

A flexible and user-friendly Python caching interface that provides a unified API for both synchronous and asynchronous caching, by wrapping and integrating two well-established caching libraries:

`cacheio` simplifies caching in Python applications by providing a consistent API for both sync and async use cases — no need to learn two different interfaces or manage separate dependencies manually. It intelligently loads only the backend dependencies you need.

---

## Overview 🚀

`cacheio` is not just another caching library. It is a **unified abstraction layer** that seamlessly bridges the gap between synchronous and asynchronous caching in Python by integrating:

- **[`cachelib`](https://github.com/pallets/cachelib)** for reliable, performant synchronous caching backends, including in-memory caches.
- **[`aiocache`](https://github.com/aio-libs/aiocache)** for flexible, feature-rich asynchronous caching, with support for multiple backends like Redis and Memcached.

This design means you can switch between sync and async caching or use both in the same codebase with a **shared, consistent API**.

---

## Installation

Install `cacheio` via pip. The library uses **optional dependency groups** to help you install only what you need.

### Basic Installation

Install the core package without any caching backends:

```bash
pip install cacheio
```

### Installing with Backends

Choose the optional group(s) based on your use case:

* **Synchronous Caching:** Use the `sync` extra to install `cachelib` and synchronous cache support.

    ```bash
    pip install "cacheio[sync]"
    ```

* **Asynchronous Caching:** Use the `async` extra to install `aiocache` and asynchronous cache support.

    ```bash
    pip install "cacheio[async]"
    ```

* **Full Installation:** Install both synchronous and asynchronous backends together.

    ```bash
    pip install "cacheio[full]"
    ```

---

## Configuration

`cacheio` exposes a global configuration object, allowing you to customize default settings like the time-to-live (TTL) for cached entries and cache size thresholds.

You can modify the configuration by importing `config` directly or by using the `configure` function which accepts a callable that modifies the global config.

### Using the Global `config` Object

You can read or update configuration parameters directly:

```python
from cacheio import config

print(config.default_ttl)  # Default TTL in seconds (e.g., 300)

# Update the default TTL to 600 seconds (10 minutes)
config.default_ttl = 600
```

### Using the `configure` Helper

Use the `configure` function to update configuration settings in a safe and explicit manner:

```python
from cacheio import configure

def update_config(cfg):
    cfg.default_ttl = 600
    cfg.default_threshold = 1000

configure(update_config)
```

This pattern can be handy for centralized configuration setup in your application.

---

## Quick Start

### Synchronous Caching

Use `CacheFactory.memory_cache()` to get a synchronous cache adapter backed by `cachelib.SimpleCache`. The adapter respects your configured TTL and cache size threshold by default.

```python
from cacheio import CacheFactory

# Create a synchronous in-memory cache adapter
my_cache = CacheFactory.memory_cache()

# Set a value with TTL 300 seconds (or your configured TTL)
my_cache.set("my_key", "my_value", ttl=300)

# Retrieve the cached value
value = my_cache.get("my_key")
print(f"Retrieved value: {value}")
```

### Asynchronous Caching

Use `CacheFactory.async_memory_cache()` to get an asynchronous cache adapter backed by `aiocache.Cache`, honoring the TTL from the config.

```python
import asyncio
from cacheio import CacheFactory

async def main():
    # Create an asynchronous in-memory cache adapter
    my_async_cache = CacheFactory.async_memory_cache()

    # Set a value with TTL 300 seconds asynchronously
    await my_async_cache.set("my_async_key", "my_async_value", ttl=300)

    # Retrieve the cached value asynchronously
    async_value = await my_async_cache.get("my_async_key")
    print(f"Retrieved async value: {async_value}")

if __name__ == "__main__":
    asyncio.run(main())
```

---

## Usage Examples

### 1. Synchronous Caching with the `cached` Decorator

`cacheio` provides decorators like `@cached` to simplify memoization of synchronous methods. In this example, we define a class inheriting from `Cacheable` that sets up a default `cachelib`-based in-memory cache.

```python
import time
from cacheio import cached
from cacheio.mixins import Cacheable

class UserService(Cacheable):
    @cached(key_fn=lambda self, user_id, **kwargs: f"user:{user_id}", ttl=60)
    def fetch_user(self, user_id: int, request_id: str) -> dict:
        print(f"Fetching user {user_id} from database...")
        time.sleep(2)  # Simulate delay
        return {"id": user_id, "name": f"User_{user_id}", "request": request_id}

user_service = UserService()

print("First call:")
user_1 = user_service.fetch_user(user_id=1, request_id="req-1")
print(f"Result: {user_1}\n")

print("Second call (cached):")
user_2 = user_service.fetch_user(user_id=1, request_id="req-1")
print(f"Result: {user_2}\n")

print("Third call (different request_id, still cached):")
user_3 = user_service.fetch_user(user_id=1, request_id="req-2")
print(f"Result: {user_3}")
```

### 2. Asynchronous Caching with the `async_cached` Decorator

Similarly, `@async_cached` works for async methods and uses the `AsyncCacheable` mixin, which sets up an `aiocache` in-memory backend.

```python
import asyncio
from cacheio import async_cached
from cacheio.mixins import AsyncCacheable

class AsyncUserService(AsyncCacheable):
    @async_cached(key_fn=lambda self, user_id, **kwargs: f"user:{user_id}", ttl=60)
    async def fetch_user(self, user_id: int, request_id: str) -> dict:
        print(f"Fetching user {user_id} asynchronously...")
        await asyncio.sleep(2)  # Simulate async delay
        return {"id": user_id, "name": f"User_{user_id}", "request": request_id}

async def main():
    user_service = AsyncUserService()

    print("First call:")
    user_1 = await user_service.fetch_user(user_id=1, request_id="req-1")
    print(f"Result: {user_1}\n")

    print("Second call (cached):")
    user_2 = await user_service.fetch_user(user_id=1, request_id="req-1")
    print(f"Result: {user_2}\n")

    print("Third call (different request_id, still cached):")
    user_3 = await user_service.fetch_user(user_id=1, request_id="req-2")
    print(f"Result: {user_3}")

if __name__ == "__main__":
    asyncio.run(main())
```

---

## Why `cacheio`?

- **Unified API** for sync and async caching.
- **Seamless backend integration** with two proven libraries: [`cachelib`](https://github.com/pallets/cachelib) and [`aiocache`](https://github.com/aio-libs/aiocache).
- **Minimal dependencies** — install only what you need.
- **Simple decorators** and mixins to add caching effortlessly.
- **Configurable defaults** with a global config object and helper.
- **Flexible TTL and backend options** via factory methods.

---

## Contributing

Contributions are welcome! Open an issue or submit a pull request on the [GitHub repository](https://github.com/bnlucas/cacheio).

---

## License

`cacheio` is licensed under the MIT License. See [LICENSE](https://github.com/bnlucas/cacheio/blob/main/LICENSE) for details.
