from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from captcha.image import ImageCaptcha

from app.services.user_services.verification_service import store_captcha_code,generate_verification_code


router = APIRouter(tags=["Captcha"])

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
    captcha_text = generate_verification_code(length=4)
    image = ImageCaptcha(width=160, height=80)
    data = image.generate(captcha_text)

    # 将图形验证码与手机号绑定并存储在 Redis 中
    store_captcha_code(phone_number, captcha_text)

    return StreamingResponse(data, media_type="image/png")
