# API endpoints for the 'user' resource.
import os
import random
import string
from datetime import timedelta
import time
from typing import Optional
from starlette.requests import Request
import logging

from fastapi import APIRouter, HTTPException, Depends
from tortoise import Tortoise, transactions
from app.schemas import PasswordUpdateModel, UserCreate, UserLogin, UserPublicModel
from app.crud import create_user, authenticate_user
from app.models.redis_config import redis_client
from app.models.shensimodels import KeyModel, User_Pydantic, UserModel
from passlib.context import CryptContext
from app.dependencies import create_access_token, get_current_user
from app.api.api_v1.endpoints.utils.smsverify import send_verification_code, store_verification_code, validate_verification_code
from starlette import status
import random
import string
from app.dependencies import ACCESS_TOKEN_EXPIRE_MINUTES
from app.models.oneapimodels import Tokens, Users
from app.api.api_v1.endpoints.utils.generate_key import generate_key
# 配置日志
logging.basicConfig(level=logging.INFO)
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
    keys_info = ['sk-' + key.key for key in bound_keys]

    # 将keys信息添加到响应中
    user_dict['bound_keys'] = keys_info

    return UserPublicModel(**user_dict)


@router.post("/users/send_verify_code")
async def send_verify_code(request: Request, mobile: str, captcha_input: str):
    """
    向指定手机号发送6位数字验证码，并验证图形验证码的正确性。
    在使用该接口前 先使用/captcha/{phone_number}获取对应手机号码的验证码
    步骤:
    1. 验证用户提交的图形验证码是否正确。
    2. 生成一个随机的6位数字验证码。
    3. 将验证码和手机号关联后存储到Redis中，并设置过期时间。
    4. 调用短信服务API发送验证码到用户手机。

    请求参数:
    - mobile (str): 用户的手机号码。
    - captcha_input (str): 用户输入的图形验证码。

    返回:
    - 成功：返回"Verification code sent successfully."消息。
    - 失败：返回相应的错误信息。
    """
    # 生成图形验证码的键
    captcha_key = f"captcha:{mobile}"

    # 从 Redis 中获取与手机号关联的图形验证码
    stored_captcha_code = redis_client.get(captcha_key)

    # 验证图形验证码
    if not stored_captcha_code or captcha_input.lower() != stored_captcha_code.lower():
        raise HTTPException(status_code=400, detail="Invalid CAPTCHA")

    # 清除 Redis 中的图形验证码，防止重复使用
    redis_client.delete(captcha_key)

    try:
        verification_code = ''.join(random.choices(string.digits, k=6))
        store_verification_code(mobile, verification_code)  # 将验证码存储到 Redis
        await send_verification_code(mobile)
        return {"message": "Verification code sent successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# 创建CryptContext实例
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@router.post("/users/register", response_model=User_Pydantic)
async def register_user(user: UserCreate):
    """
    使用给定的用户信息注册新用户，无需验证码验证。

    异常:
    - HTTPException: 400 错误，如果用户已存在。
    """
    async with transactions.in_transaction("shensidb") as shensidb_conn:
        async with transactions.in_transaction("oneapidb") as oneapidb_conn:

            # 检查用户是否已存在
            existing_user = await UserModel.get_or_none(phone_number=user.phone_number)
            if existing_user:
                raise HTTPException(
                    status_code=400, detail="User with this phone number already exists")

            existing_user = await UserModel.get_or_none(email=user.email)
            if existing_user:
                raise HTTPException(
                    status_code=400, detail="User with this email already exists")

            # 生成随机昵称（如果用户未提供）
            username = user.username if user.username else ''.join(
                random.choices(string.ascii_letters + string.digits, k=8))

            # 创建用户
            db_user = await create_user(user.email, user.phone_number, user.password, username)

            oneapi_user = await Users.create(
                username=user.username,
                password=db_user.hashed_password,  # 直接使用shensidb中的哈希密码
                display_name=user.username,  # display_name设置为与username相同
                role=1,
                status=1,  # 根据is_active字段设置status
                email=user.email,
                wechat_id=user.phone_number,  # 复制手机号
                quota=os.getenv('QUOTA'),  # 设置quota为5000000
                used_quota=0,  # 设置used_quota为0
                request_count=0,  # 设置request_count为0
                # 其他字段根据需要设置或保留默认值
                # using_db=oneapidb_conn
            )

            # 生成API key
            api_key = generate_key()
            # 在shensidb中为用户生成API key
            await KeyModel.create(
                user_id=db_user.id,
                key=api_key,
                # 其他字段根据需要设置或保留默认值
                # using_db=shensidb_conn
            )

            # 在oneapidb中为用户生成API key
            await Tokens.create(
                user_id=oneapi_user.id,  # 假设oneapidb中的用户ID与shensidb中的相同
                key=api_key,
                name="默认apikey",
                remain_quota=os.getenv('QUOTA'),
                created_time=int(time.time()),  # 当前时间戳
                accessed_time=int(time.time()),  # 当前时间戳，或根据需要设置
                # 其他字段根据需要设置或保留默认值
                using_db=oneapidb_conn
            )
    return await User_Pydantic.from_tortoise_orm(db_user)


@router.post("/users/login")
async def login_for_access_token(form_data: UserLogin):
    """
    验证用户并提供访问令牌。支持使用密码或验证码登录。

    请求参数:
    - form_data: 包含登录信息的对象，可能包括密码或验证码。

    返回:
    - 成功: 返回包含访问令牌的 JSON 对象。
    - 失败: 返回 401 错误，提示登录信息不正确。
    """
    user = None
    if form_data.password:
        # 使用密码登录
        user = await authenticate_user(form_data.login, form_data.password)
    elif form_data.verification_code:
        # 验证验证码是否正确
        if await validate_verification_code(form_data.login, form_data.verification_code):
            # 如果验证码正确，根据登录信息（手机号或邮箱）获取用户对象
            user = await UserModel.get_or_none(phone_number=form_data.login) or \
                await UserModel.get_or_none(email=form_data.login)
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid verification code",
                headers={"WWW-Authenticate": "Bearer"},
            )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect login details",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 创建访问令牌
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = await create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.put("/username")
async def update_username(new_username: str, current_user: UserModel = Depends(get_current_user)):
    """
    更新当前用户的用户名。

    参数:
    - new_username (str): 新的用户名。

    返回:
    - dict: 用户名更新成功的消息。
    """
    # 检查新用户名是否已被占用
    if await UserModel.filter(username=new_username).exists():
        raise HTTPException(
            status_code=400, detail="Username is already taken")

    current_user.username = new_username
    await current_user.save()
    return {"message": "Username updated successfully"}


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@router.put("/users/update-password")
async def update_password(password_update: PasswordUpdateModel, current_user: UserModel = Depends(get_current_user)):
    """
    改密码
    """

    # 验证旧密码
    if not pwd_context.verify(password_update.old_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Old password is incorrect")

    # 更新密码
    hashed_new_password = pwd_context.hash(password_update.new_password)
    current_user.hashed_password = hashed_new_password
    await current_user.save()

    return {"message": "Password updated successfully"}


@router.delete("/keys/{key_id}")
async def delete_user_key(key_id: int, current_user: UserModel = Depends(get_current_user)):

    """
    删除当前用户绑定的特定key。

    参数:
    - key_id (int): 要删除的key的ID。

    异常:
    - HTTPException: 404 错误，如果找不到指定的key或key不属于当前用户。

    返回:
    - dict: 成功删除key的确认消息。
    """

    # 查找要删除的key，确保它属于当前用户
    key_to_delete = await KeyModel.get_or_none(id=key_id, user_id=current_user.id)
    if not key_to_delete:
        raise HTTPException(
            status_code=404, detail="Key not found or not owned by the user")

    # 从数据库中删除key
    await key_to_delete.delete()

    return {"message": "Key deleted successfully"}
