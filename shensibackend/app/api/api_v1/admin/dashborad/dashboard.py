import logging
from tortoise.functions import Count, Sum
from datetime import datetime, timedelta
from tortoise.expressions import RawSQL
from pypika.terms import CustomFunction
from fastapi import APIRouter
from app.models.oneapimodels import (
    Tokens,
    Users,
    Logs,
)  # 确保从您的模型文件中导入Tokens和Users模型
from tortoise.contrib.fastapi import HTTPNotFoundError
from pydantic import BaseModel

router = APIRouter()


class UserQuotaUsage(BaseModel):
    user_id: int
    username: str
    total_quota: int
    used_quota: int
    remaining_quota: int


FromUnixtime = CustomFunction("DATE(FROM_UNIXTIME", ["timestamp"])


@router.get("/dashboard/user/{user_id}/quota-usage/", response_model=UserQuotaUsage)
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
            remaining_quota=0,
        )

    total_quota = sum(token.remain_quota + token.used_quota for token in tokens)
    used_quota = sum(token.used_quota for token in tokens)
    remaining_quota = sum(token.remain_quota for token in tokens)

    return UserQuotaUsage(
        user_id=user_id,
        username=user.username,
        total_quota=total_quota,
        used_quota=used_quota,
        remaining_quota=remaining_quota,
    )


@router.get("/dashboard/daily-quota-usage/")
async def daily_quota_usage():
    """
    获取每日配额使用情况的接口。
    此接口使用RawSQL手动构造SQL表达式来将created_at字段的UNIX时间戳转换为日期，并按日期进行分组。
    每组数据包含日期和该日期下所有日志记录的配额总和。
    返回的数据格式为包含日期和总配额的列表。
    """
    # 使用RawSQL手动构造SQL表达式来转换created_at字段为日期，并按日期分组
    daily_usage = (
        await Logs.annotate(
            date=RawSQL("DATE(FROM_UNIXTIME(`created_at`))"), total_quota=Sum("quota")
        )
        .group_by("date")
        .values("date", "total_quota")
    )

    return {"data": list(daily_usage)}


@router.get("/dashboard/analytics/dau/")
async def daily_active_users():
    """
    获取每日活跃用户数（DAU）的接口。
    此接口首先获取今天所有日志记录的用户ID列表，然后使用Python的set来去重，从而计算出不同用户的数量。
    返回的数据格式为包含日期和当天活跃用户数（DAU）的字典。
    """
    today = datetime.now().date()

    # 获取今天的用户ID列表
    user_ids = (
        await Logs.annotate(date=RawSQL("DATE(FROM_UNIXTIME(`created_at`))"))
        .filter(date=today)
        .values_list("user_id", flat=True)
    )

    # 使用Python的set来去重，计算不同用户的数量
    distinct_user_ids = set(user_ids)
    dau = len(distinct_user_ids)

    print(dau)
    return {"date": today.strftime("%Y-%m-%d"), "dau": dau}


# 配置日志记录
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@router.get("/dashboard/analytics/usage-habits/")
async def usage_habits():
    """
    获取用户使用习惯的接口。
    此接口分析特定日期（默认为今天）的日志记录，以了解不同类型的日志（即用户的操作类型）的使用频率。
    它通过RawSQL将created_at字段转换为日期，并按日志类型进行分组和计数。
    返回的数据格式为包含日期和各类型日志的计数列表。
    """
    today = datetime.now().date()
    logger.info("Retrieving usage habits for: %s", today)

    try:
        # 直接在查询中使用 values_list 并异步等待结果
        usage_habits_list = (
            await Logs.annotate(
                date=RawSQL("DATE(FROM_UNIXTIME(`created_at`))"), count=Count("id")
            )
            .filter(date=today)
            .group_by("type")
            .order_by("-count")
            .values_list("type", "count")
        )

        logger.info("Usage habits retrieved successfully")
    except Exception as e:
        logger.error("Error retrieving usage habits: %s", e)
        raise

    return {"date": today.strftime("%Y-%m-%d"), "usage_habits": list(usage_habits_list)}


@router.get("/dashboard/analytics/retention/")
async def retention_rate():
    """
    获取用户留存率的接口。
    此接口计算昨天新用户中有多少在今天仍然活跃，以估计留存率。
    它首先获取昨天和今天所有日志记录的用户ID列表，使用集合去重并计算两天不同用户的数量。
    然后计算两个集合的交集，即留存的用户数，并计算留存率。
    返回的数据格式为包含日期、昨天的新用户数、今天留存的用户数和留存率的字典。
    """
    today = datetime.now().date()
    yesterday = today - timedelta(days=1)

    # 获取昨天的用户ID列表
    user_ids_yesterday = (
        await Logs.annotate(date=RawSQL("DATE(FROM_UNIXTIME(`created_at`))"))
        .filter(date=yesterday)
        .values_list("user_id", flat=True)
    )

    # 获取今天的用户ID列表
    user_ids_today = (
        await Logs.annotate(date=RawSQL("DATE(FROM_UNIXTIME(`created_at`))"))
        .filter(date=today)
        .values_list("user_id", flat=True)
    )

    # 使用集合去重并计算昨天和今天不同用户的数量
    distinct_user_ids_yesterday = set(user_ids_yesterday)
    distinct_user_ids_today = set(user_ids_today)

    # 计算留存的用户数
    retained_users = distinct_user_ids_today.intersection(distinct_user_ids_yesterday)
    retained_users_count = len(retained_users)

    new_users_count = len(distinct_user_ids_yesterday)
    retention = (
        (retained_users_count / new_users_count) * 100 if new_users_count > 0 else 0
    )

    return {
        "date": today.strftime("%Y-%m-%d"),
        "new_users_yesterday": new_users_count,
        "retained_users_today": retained_users_count,
        "retention_rate": f"{retention:.2f}%",
    }
