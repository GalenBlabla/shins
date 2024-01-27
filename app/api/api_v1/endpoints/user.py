# API endpoints for the 'user' resource.
import random
import string
from datetime import timedelta
from typing import Optional
from starlette.requests import Request

from fastapi import APIRouter, HTTPException, Depends
from app.schemas import PasswordUpdateModel, UserCreate, UserLogin, UserPublicModel
from app.crud import create_user, authenticate_user
from app.models.shensimodels import KeyModel, User_Pydantic, UserModel
from passlib.context import CryptContext
from app.dependencies import create_access_token, get_current_user
from app.api.api_v1.endpoints.utils.smsverify import send_verification_code, validate_verification_code,authenticate_user_with_code
from starlette import status
import random
import string

from app.dependencies import ACCESS_TOKEN_EXPIRE_MINUTES

router = APIRouter()
@router.get("/users/me")
async def read_users_me(current_user: UserModel = Depends(get_current_user)):
    # 获取用户基本信息
    user_dict = {
        'id': current_user.id,
        'username': current_user.username,
        'email': current_user.email,
        'phone_number': current_user.phone_number,
        'is_active': current_user.is_active,
        'is_superuser': current_user.is_superuser
    }

    # 获取与用户绑定的所有keys
    bound_keys = await KeyModel.filter(user_id=current_user.id).all()

    # 将每个key的字符串值添加到列表中
    keys_info = ['sk-'+key.key for key in bound_keys]

    # 将keys信息添加到响应中
    user_dict['bound_keys'] = keys_info

    return UserPublicModel(**user_dict)



@router.post("/users/send_verify_code")
async def send_verify_code(request: Request, mobile: str, captcha_input: str):
    """
    向指定的手机号发送验证码，并要求验证图形验证码。

    参数:
    - mobile (str): 要发送验证码的手机号码。
    - captcha_input (str): 用户输入的图形验证码。

    异常:
    - HTTPException: 400 错误，手机号已经注册或图形验证码错误。
    - HTTPException: 500 错误，发送验证码时出错。

    返回:
    - dict: 成功发送验证码的确认消息。
    """
    # 验证图形验证码
    # stored_captcha_text = request.session.get('captcha_text')
    # if not stored_captcha_text or captcha_input.lower() != stored_captcha_text.lower():
    #     raise HTTPException(status_code=400, detail="Invalid CAPTCHA")

    # # 清除会话中的验证码，防止重复使用
    # request.session.pop('captcha_text', None)

    # 检查手机号是否已经注册
    existing_user = await UserModel.get_or_none(phone_number=mobile)
    if existing_user:
        raise HTTPException(status_code=400, detail="Mobile number already registered")

    try:
        # 发送手机验证码
        await send_verification_code(mobile)
        return {"message": "Verification code sent successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    
@router.post("/users/register", response_model=User_Pydantic)
async def register_user(user: UserCreate):
    """
    使用给定的用户信息注册新用户。
    
    异常:
    - HTTPException: 400 错误，用户已存在或验证码无效。
    """
    # 检查用户是否已存在
    existing_user = await UserModel.get_or_none(phone_number=user.phone_number)
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")
    
    # 验证验证码
    if not await validate_verification_code(user.phone_number, user.verification_code):
        raise HTTPException(status_code=400, detail="Invalid verification code")

    # 生成随机昵称（如果用户未提供）
    username = user.username if user.username else ''.join(random.choices(string.ascii_letters + string.digits, k=8))

    # 创建用户
    db_user = await create_user(user.email, user.phone_number, user.password, username)
    return await User_Pydantic.from_tortoise_orm(db_user)


@router.post("/users/login")
async def login_for_access_token(form_data: UserLogin):
    """
    验证用户并提供访问令牌。
    """
    user = None
    if form_data.password:
        # 使用密码登录
        user = await authenticate_user(form_data.login, form_data.password)
    elif form_data.verification_code:
        # 使用验证码登录
        user = await authenticate_user_with_code(form_data.login, form_data.verification_code)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect login details",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = await create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}



@router.put("/users/{user_id}/username")
async def update_username(user_id: int, new_username: str, current_user: UserModel = Depends(get_current_user)):
    """
    更新特定用户的用户名。
    
    返回:
    - dict: 用户名更新成功的消息。
    """
    if user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed to update this user's username")

    user = await UserModel.get(id=user_id)
    # 检查新用户名是否已被占用
    if await UserModel.filter(username=new_username).exists():
        raise HTTPException(status_code=400, detail="Username is already taken")

    user.username = new_username
    await user.save()
    return {"message": "Username updated successfully"}


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
@router.put("/users/update-password")
async def update_password(password_update: PasswordUpdateModel, current_user: UserModel = Depends(get_current_user)):
    """
    改密码
    """
    # 验证旧密码
    if not pwd_context.verify(password_update.old_password, current_user.hashed_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Old password is incorrect")

    # 更新密码
    hashed_new_password = pwd_context.hash(password_update.new_password)
    current_user.hashed_password = hashed_new_password
    await current_user.save()

    return {"message": "Password updated successfully"}
