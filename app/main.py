from contextlib import asynccontextmanager

from app.config.mysql_config import init_db
from config.logger_config import logger
from fastapi import FastAPI

from app.config.redis_config import init_redis, close_redis


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="RAG 智能对话系统",
        lifespan=lifespan,
    )

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: startup and shutdown events."""
    # Startup
    await init_redis()
    await init_db()
    yield
    # Shutdown
    await close_redis()
    await engine.dispose()







app = create_app()

logger.info("🚀 FastAPI 服务启动成功！")


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}
