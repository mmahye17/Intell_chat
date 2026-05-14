from datetime import datetime

from sqlalchemy import String, Integer, Boolean, DateTime, func, Index, VARCHAR
from sqlalchemy.orm import relationship, Mapped, mapped_column

from app.config.mysql_config import Base


class User(Base):
    __tablename__ = "users"


    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment="用户id")
    username: Mapped[str] = mapped_column(String(32), unique=True, nullable=False, index=True, comment="用户名")
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False, comment="加密后的密码")
    gender: Mapped[str] = mapped_column(String(10), nullable=True, comment="性别")
    nickname: Mapped[str] = mapped_column(String(32), nullable=True, default=None, comment="用户昵称")
    avatar: Mapped[str] = mapped_column(String(512), nullable=True, comment="头像地址")
    email: Mapped[str] = mapped_column(String(128), nullable=True, comment="邮箱")
    is_deleted: Mapped[int] = mapped_column(Integer, default=0, comment="是否被删除")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")

