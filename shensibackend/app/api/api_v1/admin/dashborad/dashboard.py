
from pypika.terms import CustomFunction
from tortoise.expressions import F
from fastapi import APIRouter
from app.models.oneapimodels import Tokens, Users, Logs  # 确保从您的模型文件中导入Tokens和Users模型
from tortoise.contrib.fastapi import HTTPNotFoundError
from pydantic import BaseModel

from tortoise.functions import Sum

router = APIRouter()


class UserQuotaUsage(BaseModel):
    user_id: int
    username: str
    total_quota: int
    used_quota: int
    remaining_quota: int




@router.get("/user/{user_id}/quota-usage/", response_model=UserQuotaUsage)
async def get_user_quota_usage(user_id: int):
    user = await Users.get_or_none(id=user_id)
    if user is None:
        raise HTTPNotFoundError(detail=f"User with id {user_id} not found")

    tokens = await Tokens.filter(user_id=user_id)
    if not tokens:
        return UserQuotaUsage(
            user_id=user_id,
            username=user.username,
            total_quota=0,
            used_quota=0,
            remaining_quota=0
        )

    total_quota = sum(token.remain_quota +
                      token.used_quota for token in tokens)
    used_quota = sum(token.used_quota for token in tokens)
    remaining_quota = sum(token.remain_quota for token in tokens)

    return UserQuotaUsage(
        user_id=user_id,
        username=user.username,
        total_quota=total_quota,
        used_quota=used_quota,
        remaining_quota=remaining_quota
    )


# 定义一个使用 MySQL FROM_UNIXTIME 函数的自定义函数
FromUnixtime = CustomFunction('FROM_UNIXTIME', ['timestamp'])

@router.get("/daily-quota-usage/")
async def daily_quota_usage():
    # 使用自定义函数转换 created_at 字段，并按日期分组
    daily_usage = await Logs.annotate(
        date=FromUnixtime(F('created_at')),
        total_quota=Sum('quota')
    ).group_by('date').values('date', 'total_quota')

    return {"data": list(daily_usage)}
