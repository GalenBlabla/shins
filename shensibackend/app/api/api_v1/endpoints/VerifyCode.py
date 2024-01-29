from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from starlette.requests import Request
from captcha.image import ImageCaptcha
import random
import string
from io import BytesIO
import base64

from app.api.api_v1.endpoints.utils.smsverify import store_captcha_code
from app.api.api_v1.endpoints.utils.generate_random_code import generate_random_code


router = APIRouter()

@router.get("/captcha/{phone_number}")
async def get_captcha(phone_number: str):
    """
    为指定的手机号生成4位数字的图形验证码，并将其存储在 Redis 中。
    
    步骤:
    1. 生成一个随机的4位数字图形验证码。
    2. 使用captcha库生成验证码图片。
    3. 将图形验证码与手机号关联后存储到Redis中，并设置过期时间。
    4. 直接返回验证码图片。

    请求参数:
    - phone_number (str): 用户的手机号码。

    返回:
    - 图形验证码图片。
    """
    captcha_text = generate_random_code(length=4)
    image = ImageCaptcha(width=160, height=80)
    data = image.generate(captcha_text)

    # 将图形验证码与手机号绑定并存储在 Redis 中
    store_captcha_code(phone_number, captcha_text)

    return StreamingResponse(data, media_type="image/png")
