from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.document import Document


async def create_document(
    db: AsyncSession,
    conversation_id: int,
    user_id: int,
    filename: str,
    file_path: str = "",
    file_size: int = 0,
    chunk_count: int = 0,
) -> Document:
    doc = Document(
        conversation_id=conversation_id,
        message_id=0,
        user_id=user_id,
        filename=filename,
        file_path=file_path,
        file_size=file_size,
        chunk_count=chunk_count,
        status="processing",
    )
    db.add(doc)
    await db.commit()
    await db.refresh(doc)
    return doc


async def update_document_status(
    db: AsyncSession, doc_id: int, status: str, chunk_count: int = 0, message_id: int = 0
):
    doc = await db.get(Document, doc_id)
    if doc:
        doc.status = status
        doc.chunk_count = chunk_count
        if message_id:
            doc.message_id = message_id
        await db.commit()


async def get_documents_by_user(db: AsyncSession, user_id: int) -> list[Document]:
    stmt = (
        select(Document)
        .where(Document.user_id == user_id)
        .order_by(Document.created_at.desc())
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def delete_document(db: AsyncSession, doc_id: int) -> bool:
    result = await db.execute(delete(Document).where(Document.id == doc_id))
    await db.commit()
    return result.rowcount > 0


async def delete_documents_by_conv(db: AsyncSession, conv_id: int):
    result = await db.execute(delete(Document).where(Document.conversation_id == conv_id))
    await db.commit()
    return result.rowcount


async def get_documents_by_conv(db: AsyncSession, conv_id: int) -> list[Document]:
    stmt = (
        select(Document)
        .where(Document.conversation_id == conv_id)
        .order_by(Document.created_at.asc())
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())
