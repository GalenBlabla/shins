from fastapi import APIRouter, Depends
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
    4. 将验证码图片编码为base64格式并返回给前端。

    请求参数:
    - phone_number (str): 用户的手机号码。

    返回:
    - 图形验证码图片的base64编码字符串。
    """
    captcha_text = generate_random_code(length=4)
    image = ImageCaptcha(width=160, height=80)
    data = image.generate(captcha_text)
    data_base64 = base64.b64encode(data.getvalue()).decode('utf-8')

    # 将图形验证码与手机号绑定并存储在 Redis 中
    store_captcha_code(phone_number, captcha_text)

    return {"image": f"data:image/png;base64,{data_base64}"}
