from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from backend.app.crud.conversation import get_conversations_by_user, delete_conversation
from backend.app.crud.message import delete_messages_by_conv, get_messages_by_conv
from backend.app.crud.document import delete_documents_by_conv, get_documents_by_conv
from backend.app.RAG.rag_service import delete_collection
from backend.app.schemas.common import success_response
from backend.app.schemas.conversation import ConversationItem
from backend.app.schemas.message import MessageItem
from backend.app.schemas.document import DocumentItem
from backend.app.utils.conversation_cache import get_recent_conversations_from_cache, set_recent_conversations_cache
from backend.app.models.conversation import Conversation


def _to_items(convs) -> list[ConversationItem]:
    return [ConversationItem.model_validate(c) for c in convs]


# 获取会话列表
async def get_conversation_list(db: AsyncSession, user_id: int, mode: str = "recent"):
    if mode == "recent":
        cached = await get_recent_conversations_from_cache(user_id)
        if cached is not None:
            return success_response("success", cached)
        convs = await get_conversations_by_user(db, user_id, days=7)
    else:
        convs = await get_conversations_by_user(db, user_id, days=None)

    items = _to_items(convs)
    return success_response("success", items)


# 获取会话详情
async def get_conversation_detail(db: AsyncSession, conv_id: int):
    conv = await db.get(Conversation, conv_id)
    if not conv:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="会话不存在")

    messages = await get_messages_by_conv(db, conv_id, limit=1000)
    documents = await get_documents_by_conv(db, conv_id)

    return success_response("success", {
        "conv_id": conv.id,
        "title": conv.title,
        "messages": [MessageItem.model_validate(m) for m in messages],
        "documents": [DocumentItem.model_validate(d) for d in documents],
    })


# 重命名会话
async def rename_conv(db: AsyncSession, conv_id: int, user_id: int, new_title: str):
    conv = await db.get(Conversation, conv_id)
    if not conv:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="会话不存在")
    conv.title = new_title
    await db.commit()

    convs = await get_conversations_by_user(db, user_id, days=7)
    items = [ConversationItem.model_validate(c).model_dump(mode='json') for c in convs]
    await set_recent_conversations_cache(user_id, items)

    return success_response("success")


# 删除会话
async def delete_conv(db: AsyncSession, conv_id: int, user_id: int):
    conv = await db.get(Conversation, conv_id)
    if not conv:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="会话不存在")

    await delete_messages_by_conv(db, conv_id)
    await delete_documents_by_conv(db, conv_id)
    delete_collection(conv_id)
    await delete_conversation(db, conv_id)

    convs = await get_conversations_by_user(db, user_id, days=7)
    items = [ConversationItem.model_validate(c).model_dump(mode='json') for c in convs]
    await set_recent_conversations_cache(user_id, items)

    return success_response("删除成功")
