from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.conversation import Message


async def create_message(
    db: AsyncSession, conversation_id: int, role: str, content: str
) -> Message:
    msg = Message(conversation_id=conversation_id, role=role, content=content)
    db.add(msg)
    await db.commit()
    await db.refresh(msg)
    return msg


async def get_messages_by_conv(
    db: AsyncSession, conversation_id: int, limit: int = 20
) -> list[Message]:
    stmt = (
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.id.desc())
        .limit(limit)
    )
    result = await db.execute(stmt)
    return list(reversed(result.scalars().all()))


async def get_messages_before(db: AsyncSession, conv_id: int, before_time, limit: int = 100) -> list[Message]:
    stmt = (
        select(Message)
        .where(Message.conversation_id == conv_id, Message.created_at < before_time)
        .order_by(Message.id.asc())
        .limit(limit)
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def delete_messages_by_conv(db: AsyncSession, conv_id: int):
    from sqlalchemy import delete
    result = await db.execute(delete(Message).where(Message.conversation_id == conv_id))
    await db.commit()
    return result.rowcount
