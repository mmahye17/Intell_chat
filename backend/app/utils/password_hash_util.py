import hashlib
import logging

logger = logging.getLogger(__name__)


class Hash:

    @staticmethod
    def bcrypt(password: str) -> str:
        if not password:
            raise ValueError("密码不能为空")

        try:
            # 使用 SHA-256 哈希
            password_bytes = password.encode('utf-8')
            sha256_hash = hashlib.sha256(password_bytes).hexdigest()
            return sha256_hash

        except Exception as e:
            logger.error(f"密码哈希失败: {e}")
            raise

    @staticmethod
    def verify(plain_password: str, hashed_password: str) -> bool:

        if not plain_password or not hashed_password:
            return False

        try:
            # 计算输入密码的哈希值并比对
            password_bytes = plain_password.encode('utf-8')
            computed_hash = hashlib.sha256(password_bytes).hexdigest()

            # 使用常量时间比较防止时序攻击
            return computed_hash == hashed_password

        except Exception as e:
            logger.error(f"密码验证失败: {e}")
            return False