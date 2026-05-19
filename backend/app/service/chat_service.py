import os
import uuid
from pathlib import Path
from fastapi import HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from backend.app.utils.conversation_cache import get_recent_conversations_from_cache
from backend.app.models.conversation import Conversation

from backend.app.config.Global_config import LLM_MODEL, LLM_API_KEY, LLM_BASE_URL, CONVERSION_ROUNDS_SIZE, RETRIEVER_TOP_K, \
    RERANK_TOP_N
from backend.app.crud import conversation as conv_crud
from backend.app.crud.message import create_message, get_messages_by_conv, get_messages_before
from backend.app.crud.document import create_document, update_document_status
from backend.app.RAG.rag_service import load_documents, split_documents, store_documents, retrieve_with_rerank, hybrid_search
from backend.app.schemas.common import success_response
from backend.app.schemas.message import MessageItem, SourceItem
from backend.app.utils.conversation_cache import set_recent_conversations_cache
from backend.app.config.logger_config import logger

FILE_DATA_DIR = Path(__file__).resolve().parent.parent / "file_data"

_llm = ChatOpenAI(
    api_key=LLM_API_KEY,
    base_url=LLM_BASE_URL,
    model=LLM_MODEL,
)


def _build_messages(history: list, question: str, sources: list[dict], summary: str | None = None, full_text: str | None = None) -> list:
    msgs = []

    system_parts = ["你是一个智能助手，请根据以下信息作为参考回答用户的问题。"
                    "只需要回答就行了，不需要带标题第几个文档"]
    if summary:
        system_parts.append(f"\n【历史对话摘要】\n{summary}")
    if full_text:
        system_parts.append(f"\n【上传文件完整内容】\n{full_text}")
    if sources:
        docs_text = "\n".join(f"【文档片段{i+1}】{s['content']}" for i, s in enumerate(sources))
        system_parts.append(f"\n【文档相关片段】\n{docs_text}")
    msgs.append(SystemMessage(content="\n".join(system_parts)))

    if history:
        for m in history:
            if m.role == "user":
                msgs.append(HumanMessage(content=m.content))
            elif m.role == "assistant":
                msgs.append(AIMessage(content=m.content))

    msgs.append(HumanMessage(content=question))
    return msgs


def _generate_title(query: str, ai_reply: str) -> str:
    try:
        resp = _llm.invoke(
            f"根据以下对话内容，生成一个15字以内的简短标题，只返回标题本身不要标点：\n用户：{query}\n助手：{ai_reply}"
        )
        return resp.content.strip()[:20] or "新对话"
    except Exception:
        return "新对话"


def _do_search(conv_id: int, query: str, mode: str):
    if mode == "hybrid":
        return hybrid_search(conv_id, query, RETRIEVER_TOP_K, RERANK_TOP_N)
    return retrieve_with_rerank(conv_id, query, RETRIEVER_TOP_K, RERANK_TOP_N)


async def send_message(
    db: AsyncSession,
    user_id: int,
    conv_id: int | None,
    query: str,
    file: UploadFile | None = None,
    retrieval_mode: str = "vector",
):
    is_new_conversion = 0
    # 1. 新建会话
    if not conv_id:
        conv = await conv_crud.create_conversation(db, user_id)
        conv_id = conv.id
        is_new_conversion = 1

    # 2. 处理文件
    sources = []
    doc_id = 0
    chunk_count = 0
    full_text = None
    if file:
        file_bytes = await file.read()
        try:
            # 保存到磁盘
            os.makedirs(FILE_DATA_DIR, exist_ok=True)
            safe_name = f"{user_id}_{uuid.uuid4().hex[:8]}_{file.filename}"
            file_path = FILE_DATA_DIR / safe_name
            with open(file_path, "wb") as f:
                f.write(file_bytes)

            # 解析全文内容
            docs = load_documents(file.filename or "file", file_bytes)
            full_text = "\n".join(d.page_content for d in docs)

            # 切片 → 向量化 → ChromaDB
            chunks = split_documents(docs)
            chunk_count = len(chunks)
            store_documents(conv_id, chunks)

            # 存数据库
            doc = await create_document(db, conv_id, user_id, file.filename or "", str(file_path), len(file_bytes), chunk_count)
            doc_id = doc.id

            # RAG 检索
            sources = _do_search(conv_id, query, retrieval_mode)
        except Exception as e:
            logger.error(f"文件处理失败: {e}")
            if doc_id:
                await update_document_status(db, doc_id, "failed", chunk_count=chunk_count)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"文件处理失败: {str(e)}",
            )

    # 3.1 构建记忆上下文（10论对话之前的摘要）
    summary = None
    history = None
    message_count = 0
    final_title = ""
    if not is_new_conversion:
        # 先从 Redis 7天会话缓存里找
        recent = await get_recent_conversations_from_cache(user_id)
        if recent:
            for item in recent:
                if item.get("id") == conv_id:
                    summary = item.get("summary")
                    message_count = item.get("message_count")
                    final_title = item.get("title", "")
                    break
        # Redis 没找到 → 查数据库
        if not summary:
            _conv = await db.get(Conversation, conv_id)
            if _conv:
                summary = _conv.summary
                message_count = _conv.message_count
                final_title = _conv.title
    # 3.2 构建记忆上下文（近10轮对话）
        history = await get_messages_by_conv(db, conv_id, CONVERSION_ROUNDS_SIZE*2)

    # 没有文件时也尝试检索 RAG（如果该会话有历史文档）
    if not is_new_conversion:   # 旧对话才进入
        if not sources:
            sources = _do_search(conv_id, query, retrieval_mode)

    # 4. 调 LLM
    messages = _build_messages(history, query, sources, summary, full_text)
    try:
        resp = _llm.invoke(messages)
        ai_reply = resp.content or ""
    except Exception as e:
        logger.error(f"LLM 调用失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI 服务异常: {str(e)}",
        )

    # 5. 存消息
    user_msg = await create_message(db, conv_id, "user", query)
    assistant_msg = await create_message(db, conv_id, "assistant", ai_reply)

    # 更新文档关联
    if doc_id:
        await update_document_status(db, doc_id, "completed", chunk_count=chunk_count, message_id=user_msg.id)

    # 6. 更新会话
    window_size = CONVERSION_ROUNDS_SIZE * 2
    message_count += 2  # user + assistant

    last_msg = ai_reply[:150] if ai_reply else ""
    update_kwargs = {"last_message": last_msg, "message_count": message_count}
    if is_new_conversion:
        final_title = _generate_title(query, ai_reply)
        update_kwargs["title"] = final_title
    await conv_crud.update_conversation(db, conv_id, **update_kwargs)

    # 7. 摘要（message_count 满一个窗口触发）
    if message_count == window_size:
        old_msgs = await get_messages_before(db, conv_id, history[0].created_at, limit=window_size)
        new_summary = summary

        if old_msgs:
            old_text = "\n".join(f"{m.role}: {m.content}" for m in old_msgs)
            if summary:
                prompt = f"已有摘要：{summary}\n\n将以下对话合并压缩为200字以内的摘要：\n{old_text}"
            else:
                prompt = f"请将以下对话压缩为200字以内的摘要：\n{old_text}"
            try:
                summary_resp = _llm.invoke(prompt)
                new_summary = summary_resp.content or ""
            except Exception:
                pass

        await conv_crud.update_conversation(db, conv_id, summary=new_summary, message_count=0)

    # 8. 更新 Redis 缓存
    convs = await conv_crud.get_conversations_by_user(db, user_id, days=7)
    from backend.app.schemas.conversation import ConversationItem
    items = [ConversationItem.model_validate(c).model_dump(mode='json') for c in convs]
    await set_recent_conversations_cache(user_id, items)

    return success_response("success", {
        "conv_id": conv_id,
        "title": final_title,
        "user_message": MessageItem.model_validate(user_msg),
        "assistant_message": MessageItem.model_validate(assistant_msg),
        "sources": [SourceItem(**s) for s in sources],
    })
