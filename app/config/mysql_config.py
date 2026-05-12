from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from Global_config import *
from sqlalchemy.orm import declarative_base

# 创建异步引擎
async_engine = create_async_engine(
    DATABASE_URL,
    echo=MYSQL_ECHO,
    pool_size=MYSQL_POOL_SIZE,
    max_overflow=MYSQL_MAX_OVERFLOW,
)

# 创建异步会话工厂
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

Base = declarative_base()


async def init_db():
    """Create all tables in the database."""
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)