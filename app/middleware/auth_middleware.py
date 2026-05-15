from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from starlette.requests import Request
from jose import JWTError

from app.utils.jwt_util import decode_token
from app.utils.session_cache import validate_token

WHITELIST = {
    "/",
    "/api/users/login",
    "/api/users/register",
    "/api/users/logout",
    #调试文档的path：
    "/docs",
    "/docs/oauth2-redirect",
    "/redoc",
    "/openapi.json",
}


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.url.path in WHITELIST:
            return await call_next(request)

        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return JSONResponse(
                status_code=401,
                content={"code": 401, "message": "未提供认证令牌"},
            )

        token = auth_header.split(" ", 1)[1]

        try:
            payload = decode_token(token)
        except JWTError:
            return JSONResponse(
                status_code=401,
                content={"code": 401, "message": "令牌无效"},
            )

        if payload.get("type") != "access":
            return JSONResponse(
                status_code=401,
                content={"code": 401, "message": "令牌类型错误"},
            )

        user_id = int(payload["sub"])

        if not await validate_token(token):
            return JSONResponse(
                status_code=401,
                content={"code": 401, "message": "会话已过期，请重新登录"},
            )

        request.state.user_id = user_id
        request.state.username = payload["username"]
        return await call_next(request)
