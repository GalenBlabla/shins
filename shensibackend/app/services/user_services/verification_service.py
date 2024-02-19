import random
import string
from typing import Optional
from app.services.utils.smsverify import send_verification_code as send_sms
from app.models.redis_config import redis_client


def generate_verification_code(length: int = 6) -> str:
    """
    生成指定长度的随机数字验证码。

    :param length: 验证码的长度，默认为6位。
    :return: 生成的随机数字验证码。
    """
    return "".join(random.choices(string.digits, k=length))


async def send_and_store_verification_code(mobile: str):
    """
    生成验证码，将其与手机号关联后存储到Redis中，并发送到用户手机。

    :param mobile: 用户的手机号码。
    """
    try:
        code = generate_verification_code()
        store_verification_code(mobile, code)
        await send_sms(mobile, code)
    except Exception as e:
        # 处理或记录异常
        print(f"Error sending or storing verification code for {mobile}: {e}")
        # 根据情况，可能需要重新抛出异常或处理错误
        raise


def validate_captcha(mobile: str, input_captcha: str) -> bool:
    """
    验证用户输入的图形验证码是否正确。

    :param mobile: 用户的手机号码。
    :param input_captcha: 用户输入的图形验证码。
    :return: 验证成功返回True，否则返回False。
    """
    try:
        captcha_key = f"captcha:{mobile}"
        stored_captcha = redis_client.get(captcha_key)
        is_valid = stored_captcha and stored_captcha.lower() == input_captcha.lower()
        if is_valid:
            redis_client.delete(captcha_key)
        return is_valid
    except Exception as e:
        print(f"Error validating captcha for {mobile}: {e}")
        return False


def store_verification_code(
    phone_number: str, code: str, expiration_in_seconds: int = 600
) -> None:
    """
    将验证码与手机号关联并存储在 Redis 中。

    :param phone_number: 接收验证码的手机号。
    :param code: 发送给用户的验证码。
    :param expiration_in_seconds: 验证码在 Redis 中的过期时间，默认为 1 分钟（60 秒）。
    """
    print("save:",phone_number,code)#save: 18009082890 106320
    try:
        redis_client.set(phone_number, code, ex=expiration_in_seconds)
        a = get_stored_verification_code(phone_number)
        print("get:",a)#get: 106320
    except Exception as e:
        print(f"Error storing verification code for {phone_number}: {e}")
        raise


def get_stored_verification_code(phone_number: str) -> Optional[str]:
    """
    从 Redis 中检索与手机号关联的验证码。

    :param phone_number: 用户的手机号。
    :return: 存储的验证码，如果没有找到则为 None。
    """
    try:
        return redis_client.get(phone_number)
    except Exception as e:
        print(f"Error retrieving stored verification code for {phone_number}: {e}")
        return None


def clear_stored_verification_code(phone_number: str) -> None:
    """
    删除存储在 Redis 中的验证码。

    :param phone_number: 用户的手机号。
    """
    try:
        redis_client.delete(phone_number)
    except Exception as e:
        print(f"Error clearing stored verification code for {phone_number}: {e}")


def store_captcha_code(
    phone_number: str, captcha_code: str, expiration_in_seconds: int = 60
):
    """
    将图形验证码与手机号关联并存储在 Redis 中。

    :param phone_number: 用户的手机号码。
    :param captcha_code: 生成的图形验证码。
    :param expiration_in_seconds: 验证码的过期时间，默认为 5 分钟。
    """
    try:
        captcha_key = f"captcha:{phone_number}"
        redis_client.set(captcha_key, captcha_code, ex=expiration_in_seconds)
    except Exception as e:
        print(f"Error storing captcha code for {phone_number}: {e}")
        raise
