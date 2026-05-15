from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

from app.config.mysql_config import get_session
from app.schemas.common import success_response
from app.schemas.users import UserResquest, LoginRequest, UserInfo
from app.service.users_service import registers, login, logout, get_user_info, update_user_info

users_router = APIRouter(prefix="/api/users", tags=["用户"])
security = HTTPBearer(auto_error=False)

@users_router.post("/register")
async def register_route(user_data: UserResquest, db: AsyncSession = Depends(get_session)):
    return await registers(user_data, db)


@users_router.post("/login", response_model=success_response)
async def login_route(req: LoginRequest, db: AsyncSession = Depends(get_session),
                      credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials if credentials else None
    return await login(db, req.username, req.password, token)


@users_router.post("/logout", response_model=success_response)
async def logout_route(req: LoginRequest, db: AsyncSession = Depends(get_session),
                      credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials if credentials else None
    return await logout(db, req, token)

@users_router.put("/user_info")
async def update_user_route(update_data: UserInfo, request: Request,
                            db: AsyncSession = Depends(get_session),
                            credentials: HTTPAuthorizationCredentials = Depends(security)):
    return await update_user_info(db, request.state.user_id, update_data)


@users_router.get("/{id}")
async def get_user_route(id: int, db: AsyncSession = Depends(get_session),
                         credentials: HTTPAuthorizationCredentials = Depends(security)):
    return await get_user_info(db, id)
