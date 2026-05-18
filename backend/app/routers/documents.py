from fastapi import APIRouter, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

from backend.app.config.mysql_config import get_session
from backend.app.service.document_service import list_documents, delete_document

doc_router = APIRouter(prefix="/api/documents", tags=["文档"])
security = HTTPBearer(auto_error=False)


@doc_router.get("/list")
async def list_route(request: Request, db: AsyncSession = Depends(get_session),
                     credentials: HTTPAuthorizationCredentials = Depends(security)):
    return await list_documents(db, request.state.user_id)


@doc_router.delete("/{doc_id}")
async def delete_route(doc_id: int, db: AsyncSession = Depends(get_session),
                       credentials: HTTPAuthorizationCredentials = Depends(security)):
    return await delete_document(db, doc_id)
