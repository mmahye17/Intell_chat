from pathlib import Path
import os
from dotenv import load_dotenv

BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
ENV_PATH = BACKEND_DIR / '.env'

load_dotenv(ENV_PATH)

#数据库配置读取
DATABASE_URL = (f"mysql+aiomysql://{os.getenv("MYSQL_USER")}"
                f":{os.getenv("MYSQL_PASSWORD")}@{os.getenv("MYSQL_HOST")}"
                f":{os.getenv("MYSQL_PORT")}/{os.getenv("MYSQL_DATABASE")}?charset=utf8mb4")

MYSQL_POOL_SIZE=os.getenv("MYSQL_POOL_SIZE", 10)
MYSQL_MAX_OVERFLOW=os.getenv("MYSQL_MAX_OVERFLOW", 20)
MYSQL_ECHO=os.getenv("MYSQL_ECHO", True)


#redis配置读取































