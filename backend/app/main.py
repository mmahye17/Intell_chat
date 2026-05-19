from contextlib import asynccontextmanager

from fastapi.security import HTTPBearer
from starlette.middleware.cors import CORSMiddleware
from backend.app.models import user, conversation, document
from backend.app.config.Global_config import APP_NAME, APP_VERSION
from backend.app.config.mysql_config import init_db, async_engine
from backend.app.config.logger_config import logger
from fastapi import FastAPI

from backend.app.config.redis_config import init_redis, close_redis

from backend.app.routers.users import users_router
from backend.app.routers.conversation import conv_router
from backend.app.routers.chat import chat_router
from backend.app.routers.documents import doc_router

from backend.app.middleware.auth_middleware import AuthMiddleware

security = HTTPBearer(auto_error=False)

@asynccontextmanager
async def lifespan(fastapi: FastAPI):
    # Startup
    await init_redis()
    await init_db()
    yield
    # Shutdown
    await close_redis()
    await async_engine.dispose()


def create_app() -> FastAPI:
    fastapi = FastAPI(
        title="RAG 智能对话系统",
        lifespan=lifespan,
    )

    # Auth middleware (先加 → 后执行)
    fastapi.add_middleware(AuthMiddleware)

    # CORS middleware (后加 → 先执行，拦截 OPTIONS)
    fastapi.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:8001",
            "http://127.0.0.1:8000",
            "http://localhost:5174",
            "http://127.0.0.1:5174",
            "http://localhost:8080"
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    fastapi.include_router(users_router)
    fastapi.include_router(conv_router)
    fastapi.include_router(chat_router)
    fastapi.include_router(doc_router)

    return fastapi


app = create_app()

logger.info("🚀 FastAPI 服务启动成功！")

@app.get("/")
async def health_check():
    return {
        "code": 0,
        "message": "RAG 智能对话系统运行正常",
        "data": {
            "app_name": APP_NAME,
            "version": APP_VERSION,
        },
    }
