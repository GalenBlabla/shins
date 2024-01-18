# API endpoints for the 'user' resource.
import random
import string
from datetime import timedelta
from typing import Optional

from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from app.schemas import UserCreate, UserLogin
from app.crud import create_user, authenticate_user
from app.models import User_Pydantic, UserModel
from app.dependencies import create_access_token, get_current_user
from starlette import status

from app.dependencies import ACCESS_TOKEN_EXPIRE_MINUTES

router = APIRouter()
# 这是一个简化的示例，实际实现将更复杂
async def send_verification_code(email_or_phone: str):
    # 生成验证码并发送到邮箱或手机
    pass

async def verify_code(email_or_phone: str, code: str) -> bool:
    # 验证收到的验证码
    return True

async def authenticate_user_with_code(login: str, code: str) -> Optional[UserModel]:
    # 实现使用验证码验证用户的逻辑
    pass

@router.post("/users/register", response_model=User_Pydantic)
async def register_user(user: UserCreate):
    if not await verify_code(user.email, user.verification_code):
        raise HTTPException(status_code=400, detail="Invalid verification code")

    # 生成随机昵称
    username = ''.join(random.choices(string.ascii_letters + string.digits, k=8))

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
    return current_user

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

