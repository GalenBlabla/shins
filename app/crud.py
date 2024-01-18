# CRUD operations (Create, Read, Update, Delete) using Tortoise ORM.

from tortoise.exceptions import DoesNotExist
from app.models import UserModel, KeyModel
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def create_user(email: str, phone_number: str, password: str, username: str):
    hashed_password = pwd_context.hash(password)
    user = await UserModel.create(email=email, phone_number=phone_number, hashed_password=hashed_password, username=username)
    return user

async def authenticate_user(username: str, password: str):
    try:
        user = await UserModel.get(username=username)
        if pwd_context.verify(password, user.hashed_password):
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
