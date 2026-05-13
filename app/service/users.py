from fastapi import HTTPException

from fastapi import Depends

from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.config.mysql_config import get_session
from app.crud.users import get_user_by_username, create_user
from app.schemas.users import UserResquest, UserInfo, UserAuthResponse
from app.utils.enc import Hash
from app.utils.random_nickname import get_random_nickname


async def registers (user_data: UserResquest,db: AsyncSession = Depends(get_session)):
    user_exist = await get_user_by_username(db, user_data.username)
    if user_exist:
        raise HTTPException(status_code = status.Http_400_BAD_REQUEST, detail = "用户已存在")
    enc_password = Hash.bcrypt(user_data.password)
    nick_name = get_random_nickname(12)
    user_info = UserInfo(username=user_data.username,password_hash=enc_password,nickname=nick_name)
    user = await create_user(db, user_info)      #返回的是orm对象
    user_info = user_info.model_validate(user)   #orm对象转换成pydantic对象
    return UserAuthResponse(token="", userInfo=user_info)
































