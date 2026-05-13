from typing import Optional

from pydantic import BaseModel, Field, ConfigDict

#用于接收前端的user数据
class UserResquest(BaseModel):
    username: str
    password: str

class UserInfoBase(BaseModel):
    nickname: Optional[str] = Field(None,max_length=20, description="昵称")
    gender: Optional[str] = Field(None,max_length=10, description="性别")
    avatar: Optional[str] = Field(None,max_length=100, description="头像")
    email: Optional[str] = Field(None,max_length=100, description="邮箱")
    is_deleted: Optional[bool] = Field(None, description="是否删除")
    created_at: Optional[str] = Field(None, description="创建时间")
    updated_at: Optional[str] = Field(None, description="更新时间")
    password_hash: Optional[str] = Field(None, description="加密的密码")

class UserInfo(UserInfoBase):
    id: int
    username: str

    model_config = ConfigDict(
        from_attributes=True  # 允许从orm对象属性中取值
    )


class UserAuthResponse(BaseModel):
    token: str
    user_info: UserInfo = Field(..., alias="userInfo")

    model_config = ConfigDict(
        populate_by_name=True, # alias和字段名兼容
        from_attributes=True    #允许从orm对象属性中取值
    )