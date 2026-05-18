from typing import Literal

from fastapi import APIRouter, Depends, Query
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

from app.config.mysql_config import get_session
from app.service.conversation_service import get_conversation_list, delete_conv, get_conversation_detail, rename_conv
from app.schemas.conversation import ConversationRename

conv_router = APIRouter(prefix="/api/conversations", tags=["会话"])
security = HTTPBearer(auto_error=False)


@conv_router.get("/list")
async def list_conversations(mode: Literal["recent", "all"] = Query(default="recent"), request: Request = None,
                             db: AsyncSession = Depends(get_session),
                             credentials: HTTPAuthorizationCredentials = Depends(security)):
    return await get_conversation_list(db, request.state.user_id, mode)


@conv_router.get("/{conv_id}")
async def get_conversation_detail_route(conv_id: int, db: AsyncSession = Depends(get_session),
                                        credentials: HTTPAuthorizationCredentials = Depends(security)):
    return await get_conversation_detail(db, conv_id)


@conv_router.put("/{conv_id}")
async def rename_conversations(conv_id: int, req: ConversationRename, request: Request,
                               db: AsyncSession = Depends(get_session),
                               credentials: HTTPAuthorizationCredentials = Depends(security)):
    return await rename_conv(db, conv_id, request.state.user_id, req.title)


@conv_router.delete("/{conv_id}")
async def delete_conversations(conv_id: int, request: Request, db: AsyncSession = Depends(get_session),
                               credentials: HTTPAuthorizationCredentials = Depends(security)):
    return await delete_conv(db, conv_id, request.state.user_id)
