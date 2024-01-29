import random
import string


def generate_random_code(length: int = 6) -> str:
    """
    生成指定长度的随机数字验证码。

    :param length: 验证码的长度，默认为6。
    :return: 生成的随机数字验证码。
    """
    return ''.join(random.choices(string.digits, k=length))
