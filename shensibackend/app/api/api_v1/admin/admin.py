from fastapi import APIRouter, HTTPException, status
from app.models.oneapimodels import Tokens, Tokens_Pydantic, TokensIn_Pydantic, Users, Users_Pydantic, UsersIn_Pydantic
from tortoise.exceptions import IntegrityError
import uuid
import random
import time

router = APIRouter()

key_chars = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"


def init_random_seed():
    """初始化随机数生成器的种子"""
    random.seed(time.time())


def get_uuid():
    """生成去除'-'的UUID字符串，并转换为大写"""
    return str(uuid.uuid4()).replace('-', '').upper()


def generate_key():
    """生成一个包含随机字符串和UUID的Token"""
    init_random_seed()  # 初始化随机种子
    key_part = ''.join(random.choice(key_chars)
                       for _ in range(16))  # 生成16字符的随机字符串
    uuid_part = get_uuid()  # 获取UUID
    # 将UUID中的偶数位置的大写字母转换为小写（模仿Go代码的逻辑）
    uuid_processed = ''.join(c.lower() if i %
                             2 == 0 else c for i, c in enumerate(uuid_part))
    return key_part + uuid_processed  # 拼接并返回


@router.post("/register/", response_model=Users_Pydantic)
async def register_user(user: UsersIn_Pydantic):
    try:
        user_obj = await Users.create(**user.dict(exclude_unset=True))
        return await Users_Pydantic.from_tortoise_orm(user_obj)
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在或其他约束冲突。",
        )


@router.post("/add-token/{user_id}/", response_model=Tokens_Pydantic)
async def add_token(user_id: int, token: TokensIn_Pydantic):
    user = await Users.get_or_none(id=user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在。",
        )

    token_data = token.dict(exclude_unset=True)
    token_data.update({
        "user_id": user_id,  # 确保Token与用户关联
        "key": generate_key(),  # 使用自定义函数生成Token key
        "created_time": int(time.time()),  # 设置当前时间戳为创建时间
    })
    token_obj = await Tokens.create(**token_data)
    return await Tokens_Pydantic.from_tortoise_orm(token_obj)
