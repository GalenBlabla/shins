# import os
# from dotenv import load_dotenv
# from tortoise import Tortoise
# from passlib.context import CryptContext
# from fastapi import APIRouter, HTTPException, status
# from app.models.oneapimodels import Tokens, Tokens_Pydantic, TokensIn_Pydantic, Users, Users_Pydantic, UsersIn_Pydantic
# from app.models.shensimodels import Key_Pydantic, KeyModel, UserModel
# from tortoise.exceptions import IntegrityError
# import uuid
# import random
# import time

# from app.schemas import KeyIn_Pydantic
# load_dotenv()
# router = APIRouter()

# key_chars = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"


# def init_random_seed():
#     """初始化随机数生成器的种子"""
#     random.seed(time.time())


# def get_uuid():
#     """生成去除'-'的UUID字符串，并转换为大写"""
#     return str(uuid.uuid4()).replace('-', '').upper()


# def generate_key():
#     """生成一个包含随机字符串和UUID的Token"""
#     init_random_seed()  # 初始化随机种子
#     key_part = ''.join(random.choice(key_chars)
#                        for _ in range(16))  # 生成16字符的随机字符串
#     uuid_part = get_uuid()  # 获取UUID
#     # 将UUID中的偶数位置的大写字母转换为小写（模仿Go代码的逻辑）
#     uuid_processed = ''.join(c.lower() if i %
#                              2 == 0 else c for i, c in enumerate(uuid_part))
#     return key_part + uuid_processed  # 拼接并返回


# # 创建CryptContext实例
# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# @router.post("/register/", response_model=Users_Pydantic)
# async def register_user(user: UsersIn_Pydantic):
#     user_dict = user.dict(exclude_unset=True)
#     # 对密码进行哈希处理
#     hashed_password = pwd_context.hash(user_dict.pop('password'))
#     try:
#         # 使用哈希后的密码创建用户对象
#         user_obj = await Users.create(**user_dict, hashed_password=hashed_password)
#         return await Users_Pydantic.from_tortoise_orm(user_obj)
#     except IntegrityError:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="用户名已存在或其他约束冲突。",
#         )


# @router.post("/add-key/{user_id}/", response_model=Key_Pydantic)
# async def add_key(user_id: int, key_in: KeyIn_Pydantic, token_in: TokensIn_Pydantic):
#     # 获取shensidb数据库连接
#     shensidb_conn = Tortoise.get_connection("shensidb")

#     # 使用shensidb数据库连接查询UserModel
#     user = await UserModel.filter(id=user_id).using_db(shensidb_conn).first()
#     if user is None:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="用户不存在。",
#         )

#     # 创建KeyModel实例
#     key_data = key_in.model_dump(exclude_unset=True)
#     key_data.update({
#         "user": user,
#         "key": generate_key(),  # 假设您已经定义了generate_key函数
#     })
#     key_obj = await KeyModel.create(**key_data, using_db=shensidb_conn)

#     # 获取oneapidb数据库连接
#     oneapidb_conn = Tortoise.get_connection("oneapidb")

#     # 创建Tokens实例
#     token_data = token_in.dict(exclude_unset=True)
#     token_data.update({
#         "user_id": user_id,
#         "key": key_data["key"],  # 使用相同的key
#         # 可以添加其他需要的字段
#         "created_time": int(time.time()),  # 当前时间戳
#         "accessed_time": int(time.time()),  # 当前时间戳，或根据需要设置
#     })
#     token_obj = await Tokens.create(**token_data, using_db=oneapidb_conn)

#     return await Key_Pydantic.from_tortoise_orm(key_obj)

"""
遍历shensi数据库 找到已经注册的用户，将这些用户的登录信息转移到oneapi中 并且复制账号密码手机号  displayname和用户名是一样的 role=1 status=1 email 和shensidb中的email一样的
"""


# @router.post("/migrate_users_from_shensidb_to_oneapidb")
# async def migrate_users_from_shensidb_to_oneapidb():
#     # 获取shensidb数据库连接
#     # shensidb_conn = Tortoise.get_connection("shensidb")
#     # shensi_users = await UserModel.all().using_db(shensidb_conn)
#     shensi_users = await UserModel.all()

#     for user in shensi_users:
#         try:
#             # 在oneAPIdb中创建新用户
#             oneapi_user = await Users.create(
#                 username=user.username,
#                 password=user.hashed_password,  # 直接使用shensidb中的哈希密码
#                 display_name=user.username,  # display_name设置为与username相同
#                 role=1,
#                 status=1 if user.is_active else 0,  # 根据is_active字段设置status
#                 email=user.email,
#                 wechat_id=user.phone_number,  # 复制手机号
#                 quota=os.getenv('QUOTA'),  # 设置quota为5000000
#                 used_quota=0,  # 设置used_quota为0
#                 request_count=0,  # 设置request_count为0
#                 # 其他字段根据需要设置或保留默认值
#                 # using_db=Tortoise.get_connection("oneapidb")
#             )

#             # 生成API key
#             api_key = generate_key()

#             # 在shensidb中为迁移的用户生成API key
#             await KeyModel.create(
#                 user_id=user.id,  # 使用shensidb中的用户ID
#                 key=api_key,
#                 # 其他字段根据需要设置或保留默认值
#                 # using_db=shensidb_conn
#             )

#             # 在oneapidb中为迁移的用户生成API key
#             await Tokens.create(
#                 user_id=oneapi_user.id,  # 使用oneAPIdb中新创建的用户ID
#                 key=api_key,
#                 name="默认apikey",
#                 remain_quota=os.getenv('QUOTA'),
#                 created_time=int(time.time()),  # 当前时间戳
#                 accessed_time=int(time.time()),  # 当前时间戳，或根据需要设置
#                 # 其他字段根据需要设置或保留默认值
#                 # using_db=Tortoise.get_connection("oneapidb")
#             )

#             print(f"用户 {user.username} 已成功迁移，并在两个数据库中生成了API key。")
#         except IntegrityError:
#             print(f"迁移用户 {user.username} 时出错：用户名已存在或其他约束冲突。")
