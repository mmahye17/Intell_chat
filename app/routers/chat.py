from fastapi import APIRouter, Depends, UploadFile, File, Form
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

from app.config.mysql_config import get_session
from app.service.chat_service import send_message

chat_router = APIRouter(prefix="/api/conversations", tags=["对话"])
security = HTTPBearer(auto_error=False)


@chat_router.post("/messages")
async def send_message_route(
    query: str = Form(...),
    conv_id: int = Form(default=None),
    file: UploadFile = File(default=None),
    request: Request = None,
    db: AsyncSession = Depends(get_session),
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    return await send_message(db, request.state.user_id, conv_id or None, query, file)
