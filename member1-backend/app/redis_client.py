"""
SafeSlope-NER — Redis Client
Covers: Section 5.4 (Feature Store < 0.8ms pipeline reads),
        Section 3.4 (deduplication TTL), Section 3.5 (DLQ)
"""
from __future__ import annotations
import os
from typing import Any

try:
    import redis.asyncio as aioredis
    import redis as redis_sync
    HAS_REDIS = True
except ImportError:
    aioredis = None
    redis_sync = None
    HAS_REDIS = False

REDIS_HOST = os.environ.get("REDIS_HOST", "redis")
REDIS_PORT = int(os.environ.get("REDIS_PORT", 6379))
REDIS_DB = 0

_pool = None
_in_memory_store: dict[str, Any] = {}


class MockAsyncRedis:
    def __init__(self):
        self._store = _in_memory_store

    async def ping(self):
        return True

    async def hset(self, name: str, mapping: dict = None, **kwargs):
        if name not in self._store:
            self._store[name] = {}
        if mapping:
            self._store[name].update(mapping)
        if kwargs:
            self._store[name].update(kwargs)
        return len(mapping or {})

    async def hgetall(self, name: str):
        return self._store.get(name, {})

    async def get(self, key: str):
        return self._store.get(key)

    async def set(self, key: str, value: Any, ex: int = None, **kwargs):
        self._store[key] = value
        return True

    async def expire(self, key: str, seconds: int):
        return True

    async def delete(self, *keys):
        for k in keys:
            self._store.pop(k, None)
        return len(keys)


def get_pool():
    global _pool
    if not HAS_REDIS:
        return None
    if _pool is None:
        _pool = aioredis.ConnectionPool(
            host=REDIS_HOST,
            port=REDIS_PORT,
            db=REDIS_DB,
            decode_responses=True,
            max_connections=50,
        )
    return _pool


async def get_redis():
    if not HAS_REDIS:
        return MockAsyncRedis()
    return aioredis.Redis(connection_pool=get_pool())


async def close_redis() -> None:
    global _pool
    if _pool and HAS_REDIS:
        await _pool.aclose()
        _pool = None


if HAS_REDIS:
    redis_client = redis_sync.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        db=REDIS_DB,
        decode_responses=True,
    )
else:
    class MockSyncRedis:
        def __init__(self):
            self._store = _in_memory_store
        def ping(self):
            return True
        def get(self, k):
            return self._store.get(k)
        def set(self, k, v, **kwargs):
            self._store[k] = v
            return True
    redis_client = MockSyncRedis()
