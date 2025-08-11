"""Tests for caching functionality."""

import os
import time

from rag_startups.utils.caching import cache_result, get_redis_client


def test_fakeredis_basic():
    """Test basic fakeredis functionality."""
    # Clear any existing Redis settings
    os.environ.pop("REDIS_HOST", None)
    os.environ.pop("REDIS_PORT", None)

    # Should get fakeredis client
    redis_client = get_redis_client()
    assert redis_client is not None

    # Test basic operations
    call_count = 0

    @cache_result(ttl_seconds=60)
    def sample_function(x):
        nonlocal call_count
        call_count += 1
        return x * 2

    # Should cache the result
    result1 = sample_function(5)
    assert result1 == 10

    # Should return cached result
    result2 = sample_function(5)
    assert result2 == 10
    assert call_count == 1  # Should not have called function again


def test_ttl_cache_fallback(monkeypatch):
    """Test fallback to TTLCache when Redis is unavailable, fast."""
    # Force TTLCache path and avoid any network wait
    os.environ["REDIS_HOST"] = "nonexistent_host"
    monkeypatch.setattr(
        "rag_startups.utils.caching.get_redis_client", lambda: None, raising=True
    )

    call_count = 0

    # Use a tiny TTL so the test completes quickly
    @cache_result(ttl_seconds=0.01)
    def sample_function(x):
        nonlocal call_count
        call_count += 1
        return x * 2

    # Should use TTLCache
    result1 = sample_function(5)
    assert result1 == 10
    assert call_count == 1

    # Should return cached result
    result2 = sample_function(5)
    assert result2 == 10
    assert call_count == 1  # Should not have called function again

    # Wait briefly for TTL to expire (no long sleep)
    time.sleep(0.02)

    # Should recompute after TTL expires
    result3 = sample_function(5)
    assert result3 == 10  # Value should be same
    assert call_count == 2  # Should have called function again


def test_cache_error_handling(monkeypatch):
    """Test that functions still work when caching fails."""
    # Clear any existing Redis settings
    os.environ.pop("REDIS_HOST", None)
    os.environ.pop("REDIS_PORT", None)

    call_count = 0

    @cache_result(ttl_seconds=60)
    def sample_function(x):
        nonlocal call_count
        call_count += 1
        return x * 2

    # First call should work and cache
    result1 = sample_function(5)
    assert result1 == 10
    assert call_count == 1

    # Second call should use cache
    result2 = sample_function(5)
    assert result2 == 10
    assert call_count == 1  # Shouldn't have called function again

    # Force cache error path but fail fast without network waits by monkeypatching Redis
    import redis

    class _FailFastRedis(redis.Redis):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

        def ping(self):
            raise redis.ConnectionError("boom")

        def get(self, *a, **k):
            raise redis.ConnectionError("boom")

        def setex(self, *a, **k):
            raise redis.ConnectionError("boom")

    monkeypatch.setattr(redis, "Redis", _FailFastRedis)

    # Ensure code path goes through Redis branch
    os.environ["REDIS_HOST"] = "somehost"

    # Should still work, but will call function again
    result3 = sample_function(5)
    assert result3 == 10
    assert call_count == 2  # Should have called function again


def test_concurrent_access():
    """Test cache behavior with concurrent access."""
    from concurrent.futures import ThreadPoolExecutor

    # Clear any existing Redis settings
    os.environ.pop("REDIS_HOST", None)
    os.environ.pop("REDIS_PORT", None)

    call_count = 0

    @cache_result(ttl_seconds=60)
    def sample_function(x):
        nonlocal call_count
        call_count += 1
        time.sleep(0.1)  # Simulate some work
        return x * 2

    # Run multiple concurrent calls
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(sample_function, 5) for _ in range(10)]
        results = [f.result() for f in futures]

    # All results should be correct
    assert all(r == 10 for r in results)

    # Should have only called function once due to caching
    assert call_count == 1
