import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.conversation import Conversation


async def create_conversation(db: AsyncSession, user_id: int, title: str = "新对话") -> Conversation:
    conv = Conversation(
        conversion_name=str(uuid.uuid4()),
        user_id=user_id,
        title=title,
    )
    db.add(conv)
    await db.commit()
    await db.refresh(conv)
    return conv


async def get_conversations_by_user(
    db: AsyncSession, user_id: int, *, days: int | None = 7) -> list[Conversation]:
    stmt = select(Conversation).where(Conversation.user_id == user_id)
    if days is not None:
        since = datetime.now(timezone.utc) - timedelta(days=days)
        stmt = stmt.where(Conversation.updated_at >= since)
    stmt = stmt.order_by(Conversation.updated_at.desc())
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def delete_conversation(db: AsyncSession, conv_id: int) -> bool:
    result = await db.execute(delete(Conversation).where(Conversation.id == conv_id))
    await db.commit()
    return result.rowcount > 0


async def update_conversation(db: AsyncSession, conv_id: int, **kwargs):
    conv = await db.get(Conversation, conv_id)
    if conv:
        for key, value in kwargs.items():
            if hasattr(conv, key):
                setattr(conv, key, value)
        await db.commit()
        await db.refresh(conv)
    return conv
