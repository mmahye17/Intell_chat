from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from jose import JWTError

from app.crud.users import get_user_by_username, create_user
from app.schemas.common import success_response
from app.schemas.users import UserResquest, UserInfo, UserAuthResponse, LoginRequest
from app.utils.password_hash_util import Hash
from app.utils.jwt_util import create_access_token, decode_token
from app.utils.session_cache import create_session, delete_session, validate_token
from app.utils.random_nickname_util import get_random_nickname


# 用户注册
async def registers(user_data: UserResquest, db: AsyncSession):
    user_exist = await get_user_by_username(db, user_data.username)
    if user_exist:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="用户已存在"
        )
    enc_password = Hash.bcrypt(user_data.password)
    nick_name = get_random_nickname(12)
    user_info = UserInfo(
        username=user_data.username, password_hash=enc_password, nickname=nick_name
    )
    user = await create_user(db, user_info)
    user_info = user_info.model_validate(user)

    access_token = create_access_token(user.id, user.username)
    await create_session(user.id, access_token, user_info.model_dump(mode='json'))

    return UserAuthResponse(
        token=access_token,
        userInfo=user_info,
    )

# 用户登录
async def login(db: AsyncSession, username: str, password: str, token: str | None = None) -> success_response:
    # 带了有效 Token → 续期ttl缓存 → 成功直接返回，不查数据库
    if token:
        try:
            if await validate_token(token):
                return success_response("有效Token登录成功", token)
        except (JWTError, KeyError, ValueError):
            pass

    # 没带 Token 或 Token 无效 → 查 MySQL 验证账号密码
    user = await get_user_by_username(db, username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在，请先注册",
        )
    if not Hash.verify(password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
        )

    new_token = create_access_token(user.id, user.username)
    await create_session(user.id, new_token, UserInfo.model_validate(user).model_dump(mode='json'))

    return success_response("账号密码登录成功", new_token)

# 用户登出
async def logout(db: AsyncSession, req: LoginRequest, token: str | None = None):
    if token:
        try:
            payload = decode_token(token)
            await delete_session(int(payload["sub"]))
            return success_response("登出成功", int(payload["sub"]))
        except JWTError:
            pass

    user = await get_user_by_username(db, req.username)
    await delete_session(user.id)
    return success_response("登出成功", user.id)
