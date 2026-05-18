import json
from typing import Optional

from backend.app.config.redis_config import cache_set, cache_get, cache_delete


def _recent_key(user_id: int) -> str:
    return f"user:conversations:{user_id}"


async def get_recent_conversations_from_cache(user_id: int) -> Optional[list]:
    data = await cache_get(_recent_key(user_id))
    if data is None:
        return None
    return json.loads(data)


async def set_recent_conversations_cache(user_id: int, conversations: list):
    ttl = 7 * 86400
    await cache_set(
        _recent_key(user_id),
        json.dumps(conversations, ensure_ascii=False, default=str),
        ttl=ttl,
    )


async def invalidate_recent_cache(user_id: int):
    await cache_delete(_recent_key(user_id))
