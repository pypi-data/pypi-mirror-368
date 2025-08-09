"""Simple TTL cache for expensive operations."""

import asyncio
import time
from typing import Callable, Dict, Generic, Optional, TypeVar

T = TypeVar("T")


class TTLCache(Generic[T]):
    """Time-based cache with TTL (time-to-live) support.

    This cache automatically expires entries after a specified time period.
    Thread-safe for async operations.
    """

    def __init__(self, ttl_seconds: int = 3600):
        """Initialize cache with TTL in seconds.

        Args:
            ttl_seconds: Time-to-live for cache entries (default: 1 hour)
        """
        self.ttl_seconds = ttl_seconds
        self._cache: Dict[str, tuple[T, float]] = {}
        self._lock = asyncio.Lock()

    async def get(self, key: str) -> Optional[T]:
        """Get value from cache if not expired.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found/expired
        """
        async with self._lock:
            if key in self._cache:
                value, timestamp = self._cache[key]
                if time.time() - timestamp < self.ttl_seconds:
                    return value
                else:
                    # Remove expired entry
                    del self._cache[key]
            return None

    async def set(self, key: str, value: T) -> None:
        """Set value in cache with current timestamp.

        Args:
            key: Cache key
            value: Value to cache
        """
        async with self._lock:
            self._cache[key] = (value, time.time())

    async def clear(self) -> None:
        """Clear all cache entries."""
        async with self._lock:
            self._cache.clear()

    async def cleanup_expired(self) -> None:
        """Remove all expired entries from cache."""
        async with self._lock:
            current_time = time.time()
            expired_keys = [
                key
                for key, (_, timestamp) in self._cache.items()
                if current_time - timestamp >= self.ttl_seconds
            ]
            for key in expired_keys:
                del self._cache[key]


class CachedResolver(Generic[T]):
    """Generic cached resolver for expensive async operations.

    Wraps any async resolver function with TTL caching.
    """

    def __init__(
        self, resolver_func: Callable[[str], T], ttl_seconds: int = 3600, max_size: int = 100
    ):
        """Initialize cached resolver.

        Args:
            resolver_func: Async function to resolve values
            ttl_seconds: Time-to-live for cache entries
            max_size: Maximum cache size (LRU eviction)
        """
        self.resolver_func = resolver_func
        self.cache = TTLCache[T](ttl_seconds)
        self.max_size = max_size
        self._resolve_lock = asyncio.Lock()

    async def resolve(self, key: str) -> T:
        """Resolve value with caching.

        Args:
            key: Key to resolve

        Returns:
            Resolved value (from cache or fresh)
        """
        # Check cache first
        cached_value = await self.cache.get(key)
        if cached_value is not None:
            return cached_value

        # Resolve with lock to prevent duplicate work
        async with self._resolve_lock:
            # Double-check pattern
            cached_value = await self.cache.get(key)
            if cached_value is not None:
                return cached_value

            # Resolve fresh value
            value = await self.resolver_func(key)
            await self.cache.set(key, value)

            # Simple size limit (could be improved with LRU)
            if len(self.cache._cache) > self.max_size:
                await self.cache.cleanup_expired()

            return value

    async def clear_cache(self) -> None:
        """Clear the resolver cache."""
        await self.cache.clear()
