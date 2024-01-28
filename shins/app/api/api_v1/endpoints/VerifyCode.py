import fastapi
from fastapi import APIRouter, Depends
from starlette.requests import Request
from captcha.image import ImageCaptcha
import random
import string
from io import BytesIO
import base64

router = APIRouter()

@router.get("/captcha")
async def get_captcha(request: Request):
    captcha_text = ''.join(random.choices(string.ascii_letters + string.digits, k=5))
    image = ImageCaptcha(width=160, height=60)
    data = image.generate(captcha_text)
    data_base64 = base64.b64encode(data.getvalue()).decode('utf-8')

    # 在会话中存储验证码文本
    request.session['captcha_text'] = captcha_text

    return {"image": f"data:image/png;base64,{data_base64}"}