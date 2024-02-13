from typing import List
from fastapi import APIRouter, Depends, HTTPException
from app.api.api_v1.endpoints.utils.unix2date import timestamp_to_datetime
from app.api.api_v1.dependencies import get_current_user
from app.schemas.schemas import BindKeyRequest, UserTokenData
from app.models.shensimodels import KeyModel, UserModel
from app.models.oneapimodels import Tokens

router = APIRouter()


@router.post("/bind-key/")
async def bind_key(
    request: BindKeyRequest, user: UserModel = Depends(get_current_user)
):
    # 验证 Key 是否以 "sk-" 开头
    if not request.key.startswith("sk-"):
        raise HTTPException(status_code=400, detail="Key must start with 'sk-'")

    # 从用户提供的 key 中移除前缀 "sk-"
    stripped_key = request.key[3:]  # 移除前三个字符 "sk-"

    # 验证去除前缀的 Key 是否存在于 oneapi 数据库中
    token_obj = await Tokens.get_or_none(key=stripped_key)
    if token_obj is None:
        raise HTTPException(status_code=404, detail="Key not found in oneapi database")

    # 验证去除前缀的 Key 是否已经在 shensi 数据库的 KeyModel 中存在
    key_obj = await KeyModel.get_or_none(key=stripped_key)
    if key_obj:
        # 检查 Key 是否已被其他用户绑定
        if key_obj.user_id is not None:
            if key_obj.user_id == user.id:
                # Key 已绑定到当前用户
                return {"message": "Key is already bound to this user"}
            else:
                # Key 已被其他用户绑定
                raise HTTPException(
                    status_code=400, detail="Key is already in use by another user"
                )
    else:
        # 如果 Key 在 KeyModel 中不存在，则创建一个新的 KeyModel 实例并绑定到当前用户
        key_obj = await KeyModel.create(key=stripped_key, user_id=user.id)

    return {"message": "Key bound successfully"}


# token check users balance
@router.get("/token-data/{key}", response_model=UserTokenData)
async def get_token_data(key: str, user: UserModel = Depends(get_current_user)):
    # 这里 user 是当前登录的用户
    # 如果没有登录，get_current_user 会抛出异常

    # 从用户提供的 key 中移除前缀 "sk-"
    # 从用户提供的 key 中移除前缀 "sk-"
    stripped_key = key
    if stripped_key.startswith("sk-"):
        stripped_key = stripped_key[3:]  # 移除前三个字符 "sk-"

    # 查询 oneapi 数据库中的 Tokens 表
    token_obj = await Tokens.get_or_none(key=stripped_key)
    if token_obj is None:
        raise HTTPException(status_code=404, detail="Key not found in oneapi database")
    # 将查询结果转换为 Pydantic 模型
    token_data = UserTokenData(
        user_id=token_obj.user_id,
        used_quota=token_obj.used_quota,
        created_time=timestamp_to_datetime(token_obj.created_time),
        expired_time=timestamp_to_datetime(token_obj.expired_time),
        status=token_obj.status,
        name=token_obj.name,
        accessed_time=timestamp_to_datetime(token_obj.accessed_time)
        if token_obj.accessed_time
        else None,
        remain_quota=token_obj.remain_quota,
        unlimited_quota=token_obj.unlimited_quota,
    )
    return token_data


@router.get("/user-tokens", response_model=List[UserTokenData])
async def get_all_user_tokens_datas(user: UserModel = Depends(get_current_user)):
    """
    获取当前用户下所有的key的信息
    """
    # 从 KeyModel 获取当前用户的所有 keys
    user_keys = await KeyModel.filter(user_id=user.id).all()
    # 聚合所有 tokens 的信息
    tokens_data = []
    for key_obj in user_keys:
        # 查询 Tokens 表中对应的 token
        token_obj = await Tokens.get_or_none(key=key_obj.key)
        if token_obj:
            # 转换为 UserTokenData 对象
            token_data = UserTokenData(
                user_id=token_obj.user_id,
                used_quota=token_obj.used_quota,
                created_time=timestamp_to_datetime(token_obj.created_time),
                expired_time=timestamp_to_datetime(token_obj.expired_time),
                status=token_obj.status,
                name=token_obj.name,
                accessed_time=timestamp_to_datetime(token_obj.accessed_time)
                if token_obj.accessed_time
                else None,
                remain_quota=token_obj.remain_quota,
                unlimited_quota=token_obj.unlimited_quota,
            )
            tokens_data.append(token_data)

    return tokens_data
