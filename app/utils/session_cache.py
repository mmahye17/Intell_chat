from typing import Any

from jose import JWTError

from app.config.redis_config import cache_hset, cache_hgetall, cache_exists, cache_expire, cache_delete, cache_delete_pattern
from app.config.Global_config import REFRESH_TOKEN_EXPIRE_DAYS, REDIS_DEFAULT_TTL_SECONDS
from app.utils.jwt_util import decode_token

TTL = REFRESH_TOKEN_EXPIRE_DAYS * REDIS_DEFAULT_TTL_SECONDS


def _session_key(user_id: int) -> str:
    return f"user:login:{user_id}"


async def create_session(user_id: int, token: str, user_data: dict[str, Any] | None = None):
    session = {"token": token}
    if user_data:
        session.update(user_data)
    await cache_hset(_session_key(user_id), session, ttl=TTL)


async def get_session(user_id: int) -> dict[str, Any] | None:
    data = await cache_hgetall(_session_key(user_id))
    if not data:
        return None
    return data


async def extend_session(user_id: int) -> bool:
    key = _session_key(user_id)
    if await cache_exists(key):
        await cache_expire(key, TTL)
        return True
    return False


async def delete_session(user_id: int):
    await cache_delete(_session_key(user_id))


async def delete_all_sessions(user_id: int):
    await cache_delete_pattern(f"user:login:{user_id}:*")


async def validate_token(token: str) -> bool:
    """验证 token：JWT签名有效 + Redis会话存在且token匹配 → 续TTL"""
    try:
        payload = decode_token(token)
        if payload.get("type") != "access":
            return False
        user_id = int(payload["sub"])
        session_data = await get_session(user_id)
        if not session_data or session_data.get("token") != token:
            return False
        await cache_expire(_session_key(user_id), TTL)
        return True
    except (JWTError, KeyError, ValueError):
        return False
