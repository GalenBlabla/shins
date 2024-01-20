# CRUD operations (Create, Read, Update, Delete) using Tortoise ORM.

from tortoise.exceptions import DoesNotExist
from app.models import UserModel, KeyModel
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def create_user(email: str, phone_number: str, password: str, username: str):
    hashed_password = pwd_context.hash(password)
    user = await UserModel.create(email=email, phone_number=phone_number, hashed_password=hashed_password, username=username)
    return user

async def authenticate_user(login: str, password: str):
    try:
        # 尝试根据用户名、电子邮件或电话号码获取用户
        user = await UserModel.get_or_none(username=login) or \
               await UserModel.get_or_none(email=login) or \
               await UserModel.get_or_none(phone_number=login)

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
