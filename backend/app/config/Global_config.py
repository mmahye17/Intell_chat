from pathlib import Path
import os
from dotenv import load_dotenv

BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
ENV_PATH = BACKEND_DIR / '.env'

load_dotenv(ENV_PATH)

APP_NAME="RAG 智能对话系统"
APP_VERSION="1.0.0"
# 数据库配置读取
DATABASE_URL = (f"mysql+aiomysql://{os.getenv("MYSQL_USER")}"
                f":{os.getenv("MYSQL_PASSWORD")}@{os.getenv("MYSQL_HOST")}"
                f":{os.getenv("MYSQL_PORT")}/{os.getenv("MYSQL_DATABASE")}?charset=utf8mb4")

MYSQL_POOL_SIZE=int(os.getenv("MYSQL_POOL_SIZE", "10"))
MYSQL_MAX_OVERFLOW=int(os.getenv("MYSQL_MAX_OVERFLOW", "20"))
MYSQL_ECHO=os.getenv("MYSQL_ECHO", True).lower() == "true"


# redis配置读取
REDIS_URL = (f"redis://{os.getenv("REDIS_HOST")}:"
                      f"{os.getenv("REDIS_PORT")}/{os.getenv("REDIS_DB")}")

REDIS_POOL_SIZE=int(os.getenv("REDIS_POOL_SIZE"))
REDIS_DEFAULT_TTL_SECONDS=int(os.getenv("REDIS_DEFAULT_TTL_SECONDS"))
REDIS_RAG_TTL_SECONDS=int(os.getenv("REDIS_RAG_TTL_SECONDS"))
REDIS_RERANK_TTL_SECONDS=int(os.getenv("REDIS_RERANK_TTL_SECONDS"))

# rag配置读取
CHROMA_DB_DIR= Path(__file__).resolve().parent.parent / f'{os.getenv("CHROMA_DB_DIR")}' #./app/chroma_db
CONVERSION_ROUNDS_SIZE=int(os.getenv("CONVERSION_ROUNDS_SIZE")) # 放入提示词的最近对话轮数
RETRIEVER_TOP_K=int(os.getenv("RETRIEVER_TOP_K"))

#嵌入模型读取
EMBEDDING_MODEL=os.getenv("EMBEDDING_MODEL")           #嵌入模型
EMBEDDING_URL=os.getenv("EMBEDDING_URL")
EMBEDDING_KEY=os.getenv("EMBEDDING_KEY")
EMBEDDING_BATCH_SIZE=int(os.getenv("EMBEDDING_BATCH_SIZE")) #嵌入批大小

#rerank模型读取
RERANK_MODEL=os.getenv("RERANK_MODEL")                 #重排序模型
RERANK_TOP_N=int(os.getenv("RERANK_TOP_N"))


# llm配置读取
LLM_PROVIDER=os.getenv("LLM_PROVIDER")
LLM_API_KEY=os.getenv("LLM_API_KEY")
LLM_MODEL=os.getenv("LLM_MODEL")
LLM_BASE_URL=os.getenv("LLM_BASE_URL")
LLM_TIMEOUT_SECONDS=int(os.getenv("LLM_TIMEOUT_SECONDS"))
LLM_MAX_RETRIES=int(os.getenv("LLM_MAX_RETRIES"))

# JWT 配置读取
JWT_SECRET_KEY=os.getenv("JWT_SECRET_KEY")
ACCESS_TOKEN_EXPIRE_MINUTES=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
REFRESH_TOKEN_EXPIRE_DAYS=int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))


























