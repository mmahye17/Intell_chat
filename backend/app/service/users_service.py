from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from jose import JWTError

from backend.app.crud.users import get_user_by_username, create_user, get_user_by_id, update_user
from backend.app.schemas.common import success_response
from backend.app.schemas.users import UserResquest, UserInfo, UserAuthResponse, LoginRequest
from backend.app.utils.password_hash_util import Hash
from backend.app.utils.jwt_util import create_access_token, decode_token
from backend.app.utils.session_cache import create_session, delete_session, get_session, validate_token
from backend.app.utils.random_nickname_util import get_random_nickname


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

# 获取用户信息
async def get_user_info(db: AsyncSession, user_id: int):
    user = await get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在",
        )
    return success_response("获取成功", UserInfo.model_validate(user))


# 更新用户信息
async def update_user_info(db: AsyncSession, user_id: int, update_data: UserInfo):
    allowed = {"nickname", "gender", "avatar", "email"}
    filtered = {k: v for k, v in update_data.model_dump().items() if k in allowed}

    updated = await update_user(db, user_id, filtered)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在",
        )
    session = await get_session(user_id)
    token = session.get("token") if session else ""
    await create_session(user_id, token, UserInfo.model_validate(updated).model_dump(mode='json'))

    return success_response("更新成功", UserInfo.model_validate(updated))


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
