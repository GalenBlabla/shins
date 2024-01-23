# API endpoints for the 'user' resource.
import random
import string
from datetime import timedelta
from typing import Optional

from fastapi import APIRouter, HTTPException, Depends
from app.schemas import UserCreate, UserLogin, UserPublicModel
from app.crud import create_user, authenticate_user
from app.models.shensimodels import User_Pydantic, UserModel
from app.dependencies import create_access_token, get_current_user
from app.api.api_v1.endpoints.utils.smsverify import send_verification_code, validate_verification_code,authenticate_user_with_code
from starlette import status
import random
import string

from app.dependencies import ACCESS_TOKEN_EXPIRE_MINUTES

router = APIRouter()

@router.post("/users/send_verify_code")
async def send_verify_code(mobile: str):
    try:
        await send_verification_code(mobile)
        return {"message": "Verification code sent successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/users/register", response_model=User_Pydantic)
async def register_user(user: UserCreate):
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

@router.get("/users/me")
async def read_users_me(current_user: UserModel = Depends(get_current_user)):
    user_dict = {
        'id': current_user.id,
        'username': current_user.username,
        'email': current_user.email,
        'phone_number': current_user.phone_number,
        'is_active': current_user.is_active,
        'is_superuser': current_user.is_superuser
    }
    return UserPublicModel(**user_dict)


@router.put("/users/{user_id}/username")
async def update_username(user_id: int, new_username: str, current_user: UserModel = Depends(get_current_user)):
    if user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed to update this user's username")

    user = await UserModel.get(id=user_id)
    # 检查新用户名是否已被占用
    if await UserModel.filter(username=new_username).exists():
        raise HTTPException(status_code=400, detail="Username is already taken")

    user.username = new_username
    await user.save()
    return {"message": "Username updated successfully"}

