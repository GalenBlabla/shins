import time
from datetime import datetime
import random


def generate_order_number(user_id: int) -> str:
    # 前缀
    prefix = "ORD"

    # 日期码
    date_str = datetime.now().strftime("%Y%m%d")  # 格式化日期为 YYYYMMDD

    # 用户ID，假设用户ID不会超过9999，以保持固定长度
    user_id_str = str(user_id).zfill(4)  # 不足4位前面补0

    # 随机序列号
    random_seq = str(random.randint(1000, 9999))  # 生成四位随机数

    # 组合
    order_number = f"{prefix}{date_str}{user_id_str}{random_seq}"

    return order_number