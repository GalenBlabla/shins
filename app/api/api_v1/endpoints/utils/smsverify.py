import random
import string
import urllib.parse
import json
import urllib.request
import random
import string
from datetime import timedelta
from datetime import datetime
from typing import Optional
import pytz

from tortoise.exceptions import DoesNotExist

from app.models import UserModel, VerificationCodeModel
from app.config import SMS_ACCOUNT,SMS_API_URL,SMS_PASSWORD


# 这是一个简化的示例，实际实现将更复杂

async def send_verification_code(mobile):
    
    # Generate a random 6-digit code
    code = ''.join([str(random.randint(0, 9)) for _ in range(6)])
    tz = pytz.timezone("Asia/Shanghai") 
    
    # Define expiration time (e.g., 10 minutes from now)
    now_with_tz = datetime.now(tz)
    expiration_time = now_with_tz + timedelta(minutes=1)
    
    # Save to database
    await VerificationCodeModel.create(email_or_phone=mobile, code=code, expires_at=expiration_time)

    url = SMS_API_URL
    values = {
        'account': SMS_ACCOUNT,
        'password': SMS_PASSWORD,
        'mobile': mobile,
        'content': f'您的验证码是：{code}。请不要把验证码泄露给其他人。',
        'format': 'json',
    }

    data = urllib.parse.urlencode(values).encode('UTF8')
    req = urllib.request.Request(url, data)
    response = urllib.request.urlopen(req)
    res = response.read()


async def validate_verification_code(mobile, input_code):
    # Retrieve the latest code from the database
    try:
        verification_code = await VerificationCodeModel.filter(email_or_phone=mobile).order_by('-created_at').first()
    except DoesNotExist:
        return False

    # Check if the code matches and is not expired
    tz = pytz.timezone("Asia/Shanghai")
    now_with_tz = datetime.now(tz)
    if verification_code and verification_code.code == input_code and now_with_tz < verification_code.expires_at:
        return True
    else:
        return False

async def authenticate_user_with_code(login: str, code: str) -> Optional[UserModel]:
    # 验证验证码
    if not await validate_verification_code(login, code):
        return None

    # 根据手机号或邮箱获取用户信息
    user = await UserModel.get_or_none(phone_number=login) or \
           await UserModel.get_or_none(email=login)

    return user
