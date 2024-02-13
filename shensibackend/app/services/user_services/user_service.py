import os
import time
import random
import string

from tortoise.transactions import in_transaction
from fastapi import HTTPException, status
from passlib.context import CryptContext

from app.models.shensimodels import UserModel, KeyModel
from app.schemas.schemas import UserCreate, UserPublicModel
from app.api.api_v1.dependencies import create_user as crud_create_user
from app.models.oneapimodels import Users, Tokens
from app.services.utils.generate_key import generate_key


async def get_user_details(user_id: int) -> UserPublicModel:
    user = await UserModel.get(id=user_id)
    bound_keys = await KeyModel.filter(user_id=user_id).all()
    keys_info = ["sk-" + key.key for key in bound_keys]

    user_dict = {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "phone_number": user.phone_number,
        "is_active": user.is_active,
        "is_superuser": user.is_superuser,
        "bound_keys": keys_info,
    }

    return UserPublicModel(**user_dict)


async def register_new_user(user_data: UserCreate) -> UserModel:
    async with in_transaction("shensidb"):
        existing_user = await UserModel.get_or_none(phone_number=user_data.phone_number)
        if existing_user:
            raise ValueError("User with this phone number already exists")

        existing_user = await UserModel.get_or_none(email=user_data.email)
        if existing_user:
            raise ValueError("User with this email already exists")

        username = (
            user_data.username
            if user_data.username
            else "".join(random.choices(string.ascii_letters + string.digits, k=8))
        )
        db_user = await crud_create_user(
            user_data.email, user_data.phone_number, user_data.password, username
        )

        async with in_transaction("oneapidb") as oneapidb_conn:
            oneapi_user = await Users.create(
                username=user_data.username,
                password=db_user.hashed_password,
                display_name=user_data.username,
                role=1,
                status=1,
                email=user_data.email,
                wechat_id=user_data.phone_number,
                quota=int(os.getenv("QUOTA", "5000000")) * 7,
                used_quota=0,
                request_count=0,
            )

            api_key = generate_key()
            await KeyModel.create(user_id=db_user.id, key=api_key)
            await Tokens.create(
                user_id=oneapi_user.id,
                key=api_key,
                name="默认apikey",
                remain_quota=int(os.getenv("QUOTA", "5000000")) * 7,
                created_time=int(time.time()),
                accessed_time=int(time.time()),
                using_db=oneapidb_conn,
            )

    return db_user


async def update_user_username(user: UserModel, new_username: str) -> str:
    """
    更新用户的用户名。

    :param user: 当前用户的模型实例。
    :param new_username: 新的用户名。
    :return: 成功更新后的消息。
    :raises HTTPException: 如果新用户名已被占用。
    """
    if await UserModel.filter(username=new_username).exists():
        raise HTTPException(status_code=400, detail="Username is already taken")

    user.username = new_username
    await user.save()
    return "Username updated successfully"


# 创建CryptContext实例
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def update_user_password(
    user: UserModel, old_password: str, new_password: str
) -> str:
    """
    更新用户的密码。

    :param user: 当前用户的模型实例。
    :param old_password: 用户提供的旧密码。
    :param new_password: 用户提供的新密码。
    :return: 成功更新后的消息。
    :raises HTTPException: 如果旧密码不正确。
    """
    if not pwd_context.verify(old_password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Old password is incorrect"
        )

    user.hashed_password = pwd_context.hash(new_password)
    await user.save()
    return "Password updated successfully"
