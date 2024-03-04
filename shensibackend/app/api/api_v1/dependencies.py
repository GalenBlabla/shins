# Dependencies for FastAPI routes.

from datetime import datetime, timedelta
import os
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from app.models.shensimodels import UserModel
from app.schemas.schemas import TokenData
from dotenv import load_dotenv
from tortoise.exceptions import DoesNotExist
from app.models.shensimodels import KeyModel
from passlib.context import CryptContext

load_dotenv()

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, os.getenv("SECRET_KEY"), algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, os.getenv("SECRET_KEY"), algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = await UserModel.get(username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def create_user(email: str, phone_number: str, hashed_password: str, username: str):
    user = await UserModel.create(
        email=email,
        phone_number=phone_number,
        hashed_password=hashed_password,  # 直接使用传入的哈希密码
        username=username,
    )
    return user



async def authenticate_user(login: str, password: str):
    try:
        # 尝试根据用户名、电子邮件或电话号码获取用户
        user = (
            await UserModel.get_or_none(username=login)
            or await UserModel.get_or_none(email=login)
            or await UserModel.get_or_none(phone_number=login)
        )

        if user and pwd_context.verify(password, user.hashed_password):
            return user
    except DoesNotExist:
        return None


async def create_key(key_str: str):
    key = await KeyModel.create(key=key_str)
    return key


async def update_key(user_id: int, key_str: str):
    user = await UserModel.get(id=user_id)
    user.key.key = key_str
    await user.key.save()
    return user
