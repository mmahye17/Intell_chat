from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.mysql_config import get_session
from app.schemas.common import success_response
from app.schemas.users import UserResquest
from app.service.users import registers

users_router = APIRouter(prefix="/api/users", tags=["users"])

@users_router.post("/register", response_model = success_response)
async def register(user_data: UserResquest,db: AsyncSession = Depends(get_session)):
    data = registers(user_data, db)
    return success_response(message="注册成功", data=data)




