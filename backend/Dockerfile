FROM python:3.13-slim

WORKDIR /app

# 系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl && rm -rf /var/lib/apt/lists/*

# Python 包管理器
RUN pip install uv -i https://pypi.tuna.tsinghua.edu.cn/simple

# 先装依赖层
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

# 复制源码到 backend/ 目录，保持 import 路径 backend.app.xxx
COPY . ./backend/

# 创建数据目录
RUN mkdir -p /app/backend/app/file_data /app/backend/app/chroma_db

EXPOSE 8000

CMD ["uv", "run", "uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
