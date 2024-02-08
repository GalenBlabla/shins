from app.models.redis_config import redis_client

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