
from typing import AsyncGenerator
from app.config.mysql_config import  AsyncSessionLocal
from sqlalchemy.ext.asyncio import AsyncSession


# 获得异步会话
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session































