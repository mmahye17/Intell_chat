from fastapi import HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from backend.app.crud.document import get_documents_by_user, delete_document as crud_delete_doc
from backend.app.models.document import Document
from backend.app.schemas.common import success_response
from backend.app.schemas.document import DocumentItem
from backend.app.RAG.rag_service import delete_collection


async def list_documents(db: AsyncSession, user_id: int):
    docs = await get_documents_by_user(db, user_id)
    return success_response(
        "success", {"list": [DocumentItem.model_validate(d) for d in docs]}
    )


async def delete_document(db: AsyncSession, doc_id: int):
    doc = await db.get(Document, doc_id)
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="文档不存在"
        )
    delete_collection(doc.conversation_id)
    deleted = await crud_delete_doc(db, doc_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="删除失败"
        )
    return success_response("success")
