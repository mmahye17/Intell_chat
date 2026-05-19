from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict
from sqlalchemy import false


class LoginRequest(BaseModel):
    username: str
    password: str
    token: Optional[str] = None

class UserResquest(BaseModel):
    username: str
    password: str


class UserInfoBase(BaseModel):
    nickname: Optional[str] = Field("", max_length=20, description="昵称")
    gender: Optional[str] = Field("", max_length=10, description="性别")
    avatar: Optional[str] = Field("", max_length=100, description="头像")
    email: Optional[str] = Field("", max_length=100, description="邮箱")
    is_deleted: Optional[int] = Field(0, description="是否删除")
    created_at: Optional[datetime] = Field(None, description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")
    password_hash: Optional[str] = Field(None, description="加密的密码")


class UserInfo(UserInfoBase):
    id: Optional[int] = Field(None, description="用户id")
    username: str

    model_config = ConfigDict(from_attributes=True)


class UserAuthResponse(BaseModel):
    token: str
    token_type: str = "bearer"
    user_info: UserInfo = Field(..., alias="userInfo")

    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True,
    )
