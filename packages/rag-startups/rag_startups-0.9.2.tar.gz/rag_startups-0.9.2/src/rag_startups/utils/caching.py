import json
import logging
from functools import wraps
from threading import Lock
from typing import Any, Callable, Optional

import fakeredis
import redis
from cachetools import TTLCache

logger = logging.getLogger(__name__)

# Global variables and locks
_redis_client = None
_redis_enabled = False
_redis_lock = Lock()
_redis_host = None  # Track Redis host changes


def get_redis_client():
    """Get Redis client, falling back to fakeredis if needed."""
    global _redis_client, _redis_enabled, _redis_host

    try:
        import os

        redis_host = os.environ.get("REDIS_HOST")

        # Check if Redis host has changed
        if redis_host != _redis_host:
            _redis_client = None  # Force new connection
            _redis_host = redis_host

        if redis_host and _redis_client is None:
            # Try to connect to real Redis
            client = redis.Redis(
                host=redis_host,
                port=int(os.environ.get("REDIS_PORT", 6379)),
                decode_responses=True,
            )
            # Test connection
            client.ping()
            _redis_enabled = True
            _redis_client = client
            return client
    except Exception as e:
        logger.warning(f"Failed to connect to Redis: {e}, using fakeredis")
        _redis_enabled = False
        _redis_client = None

    # Fallback to fakeredis
    if _redis_client is None:
        _redis_enabled = False
        _redis_client = fakeredis.FakeRedis(decode_responses=True)
    return _redis_client


def _get_cache_key(
    func: Callable, args: tuple, kwargs: dict, prefix: Optional[str] = None
) -> str:
    """Generate a cache key for the given function and arguments."""
    if prefix:
        key_parts = [str(arg) for arg in args]
        key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
        return f"{prefix}:{func.__name__}:{':'.join(key_parts)}"
    return f"{func.__name__}:{str(args)}:{str(kwargs)}"


def cache_result(
    prefix: str = None, ttl_seconds: int = 3600, ttl: Optional[int] = None
) -> Callable:
    """Cache function results using Redis or TTLCache as fallback.

    Args:
        prefix: Optional prefix for cache keys
        ttl_seconds: Time to live for cached results in seconds (default: 1 hour)
        ttl: Alias for ttl_seconds for backward compatibility

    Returns:
        Decorator function that handles caching
    """
    # Use ttl if provided, otherwise use ttl_seconds
    ttl_value = ttl if ttl is not None else ttl_seconds

    def decorator(func: Callable) -> Callable:
        # Create a TTLCache specific to this function
        local_cache = TTLCache(maxsize=1000, ttl=ttl_value)
        local_lock = Lock()
        last_redis_host = None  # Track Redis host for this decorator

        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            nonlocal last_redis_host

            # Check Redis connection and clear local cache if host changed
            global _redis_enabled, _redis_client
            _redis_client = get_redis_client()

            if _redis_host != last_redis_host:
                local_cache.clear()  # Clear local cache when Redis host changes
                last_redis_host = _redis_host

            cache_key = _get_cache_key(func, args, kwargs, prefix)

            # Try Redis first if enabled
            if _redis_enabled and _redis_client is not None:
                try:
                    cached = _redis_client.get(cache_key)
                    if cached:
                        return json.loads(cached)

                    with _redis_lock:
                        # Double-check after acquiring lock
                        cached = _redis_client.get(cache_key)
                        if cached:
                            return json.loads(cached)

                        # Compute and store in Redis
                        result = func(*args, **kwargs)
                        _redis_client.setex(cache_key, ttl_value, json.dumps(result))
                        return result
                except Exception as e:
                    logger.warning(f"Redis error: {str(e)}, falling back to TTLCache")
                    _redis_enabled = False

            # Use TTLCache as fallback
            with local_lock:
                try:
                    return local_cache[cache_key]
                except KeyError:
                    # Key not in cache or expired, compute new value
                    result = func(*args, **kwargs)
                    local_cache[cache_key] = result
                    return result

        return wrapper

    return decorator


def ttl_cache(ttl: int = 3600, maxsize: int = 1000):
    """Simple TTL cache decorator using cachetools.TTLCache.

    Args:
        ttl: Time to live in seconds (default: 1 hour)
        maxsize: Maximum size of cache (default: 1000)

    Returns:
        Decorator function that handles caching
    """
    cache = TTLCache(maxsize=maxsize, ttl=ttl)
    lock = Lock()

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            key = _get_cache_key(func, args, kwargs)
            with lock:
                if key in cache:
                    return cache[key]
                result = func(*args, **kwargs)
                cache[key] = result
                return result

        return wrapper

    return decorator


def clear_cache(prefix: str = None) -> None:
    """Clear all cached values or those matching prefix."""
    try:
        if _redis_enabled and _redis_client is not None:
            if prefix:
                pattern = f"{prefix}:*"
                keys = _redis_client.keys(pattern)
                if keys:
                    _redis_client.delete(*keys)
            else:
                _redis_client.flushdb()
    except Exception as e:
        logger.error(f"Error clearing cache: {e}")


def get_cache_stats() -> dict:
    """Get statistics about the cache."""
    try:
        if _redis_enabled and _redis_client is not None:
            info = _redis_client.info()
            return {
                "type": "redis",
                "keys": _redis_client.dbsize(),
                "memory": info.get("used_memory_human"),
                "peak_memory": info.get("used_memory_peak_human"),
            }
        else:
            return {"type": "memory", "status": "disabled"}
    except Exception as e:
        logger.error(f"Error getting cache stats: {e}")
        return {"type": "unknown", "error": str(e)}


# Initialize Redis client
_redis_client = get_redis_client()
