from typing import Optional

import redis.asyncio as aioredis
from redis.asyncio import Redis


# Global Redis client (initialized at startup)
redis_client: Optional[Redis] = None


def get_redis_client() -> Redis:
    if redis_client is None:
        raise RuntimeError("Redis client has not been initialized. Call init_redis() first.")
    return redis_client


async def init_redis():
    """Create async Redis connection and verify connectivity."""
    global redis_client
    redis_client = aioredis.from_url(
        settings.REDIS_URL,
        max_connections=settings.REDIS_POOL_SIZE,
        decode_responses=True,
    )
    # Ping test
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


# ---------------------------------------------------------------------------
# Helper: enterprise key name builders
# ---------------------------------------------------------------------------

def build_session_key(token: str) -> str:
    return f"rag:session:{token}"


def build_user_search_key(user_id: int, query_md5: str) -> str:
    return f"rag:user:{user_id}:search:{query_md5}"


def build_user_rerank_key(user_id: int, query_md5: str, doc_ids_md5: str) -> str:
    return f"rag:user:{user_id}:rerank:{query_md5}:{doc_ids_md5}"


def build_chat_history_key(conversation_id: str) -> str:
    return f"rag:chat:history:{conversation_id}"


def build_doc_chunks_key(doc_id: str) -> str:
    return f"rag:doc:chunks:{doc_id}"


def build_user_conversations_key(user_id: int) -> str:
    return f"rag:user:{user_id}:conversations"


def build_upload_progress_key(task_id: str) -> str:
    return f"rag:upload:progress:{task_id}"
