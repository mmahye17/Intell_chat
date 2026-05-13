from typing import Optional
from app.config.Global_config import *
import redis.asyncio as aioredis
from redis.asyncio import Redis



redis_client: Optional[Redis] = None

def get_redis_client() -> Redis:
    if redis_client is None:
        init_redis()
    return redis_client


async def init_redis():
    global redis_client
    redis_client = aioredis.from_url(
        REDIS_URL,
        max_connections=REDIS_POOL_SIZE,
        decode_responses=True,
    )
    await redis_client.ping()


async def close_redis():
    """Gracefully close the Redis connection."""
    global redis_client
    if redis_client is not None:
        await redis_client.close()
        redis_client = None


async def cache_get(key: str) -> Optional[str]:
    """Get a value from cache by key."""
    client = get_redis_client()
    return await client.get(key)


async def cache_set(key: str, value: str, ttl: int = 600):
    """Set a key-value pair in cache with optional TTL (seconds)."""
    client = get_redis_client()
    await client.set(key, value, ex=ttl)


async def cache_delete(key: str):
    """Delete a key from cache."""
    client = get_redis_client()
    await client.delete(key)


async def cache_delete_pattern(pattern: str):
    """Delete all keys matching a glob pattern."""
    client = get_redis_client()
    keys = []
    async for key in client.scan_iter(match=pattern):
        keys.append(key)
    if keys:
        await client.delete(*keys)



