from passlib.context import CryptContext


class Hash:
    """密码加密"""
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    @staticmethod
    def bcrypt(password: str):
        return Hash.pwd_context.hash(password)

    @staticmethod
    def verify(plain_password, hashed_password):
        return Hash.pwd_context.verify(plain_password, hashed_password)








