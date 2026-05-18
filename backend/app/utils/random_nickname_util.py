import random
import string


class NicknameGenerator:
    """随机昵称生成器"""

    # 可用的字符集
    LETTERS = string.ascii_letters  # 大小写字母 a-z A-Z
    DIGITS = string.digits  # 数字 0-9
    ALPHANUMERIC = string.ascii_letters + string.digits  # 字母+数字

    @staticmethod
    def random_string(length: int = 8, use_digits: bool = True) -> str:
        """
        生成随机字符串
        :param length: 长度，默认8
        :param use_digits: 是否包含数字，默认True
        """
        chars = NicknameGenerator.ALPHANUMERIC if use_digits else NicknameGenerator.LETTERS
        return ''.join(random.choices(chars, k=length))


# 简化调用函数
def get_random_nickname(length: int = 8) -> str:
    """获取随机昵称（字母+数字）"""
    return NicknameGenerator.random_string(length)