import random
import urllib.parse
import urllib.request
import random
import os
from dotenv import load_dotenv
from typing import Optional

from tortoise.exceptions import DoesNotExist

from app.models.redis_config import redis_client
from app.api.api_v1.endpoints.utils.generate_random_code import generate_random_code

load_dotenv()


async def send_verification_code(mobile):
    
    # Generate a random 6-digit code
    code = generate_random_code(length=4)
    # Save to database
    store_verification_code(mobile, code)

    url = os.getenv("SMS_API_URL")
    values = {
        'account': os.getenv("SMS_ACCOUNT"),
        'password': os.getenv("SMS_PASSWORD"),
        'mobile': mobile,
        'content': f'您的验证码是：{code}。请不要把验证码泄露给其他人。',
        'format': 'json',
    }

    data = urllib.parse.urlencode(values).encode('UTF8')
    req = urllib.request.Request(url, data)
    response = urllib.request.urlopen(req)
    res = response.read()

def store_verification_code(phone_number: str, code: str, expiration_in_seconds: int = 60) -> None:
    """
    将验证码与手机号关联并存储在 Redis 中。

    :param phone_number: 接收验证码的手机号。
    :param code: 发送给用户的验证码。
    :param expiration_in_seconds: 验证码在 Redis 中的过期时间，默认为 1 分钟（60 秒）。
    """
    redis_client.set(phone_number, code, ex=expiration_in_seconds)
    
def get_stored_verification_code(phone_number: str) -> Optional[str]:
    """
    从 Redis 中检索与手机号关联的验证码。

    :param phone_number: 用户的手机号。
    :return: 存储的验证码，如果没有找到则为 None。
    """
    return redis_client.get(phone_number)

def clear_stored_verification_code(phone_number: str) -> None:
    """
    删除存储在 Redis 中的验证码。

    :param phone_number: 用户的手机号。
    """
    redis_client.delete(phone_number)

def store_captcha_code(phone_number: str, captcha_code: str, expiration_in_seconds: int = 60):
    """
    将图形验证码与手机号关联并存储在 Redis 中。

    :param phone_number: 用户的手机号码。
    :param captcha_code: 生成的图形验证码。
    :param expiration_in_seconds: 验证码的过期时间，默认为 5 分钟。
    """
    captcha_key = f"captcha:{phone_number}"
    redis_client.set(captcha_key, captcha_code, ex=expiration_in_seconds)

async def validate_verification_code(phone_number: str, input_code: str) -> bool:
    """
    验证给定手机号的验证码是否正确。

    :param phone_number: 用户的手机号码。
    :param input_code: 用户输入的验证码。
    :return: 验证码正确返回 True，否则返回 False。
    """
    # 从 Redis 中获取存储的验证码
    stored_code = redis_client.get(phone_number)

    # 验证验证码是否匹配且未过期
    if stored_code and stored_code == input_code:
        # 验证成功后，清除 Redis 中的验证码，以防重复使用
        redis_client.delete(phone_number)
        return True
    else:
        return False