import uuid
import random
import time

key_chars = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"


def init_random_seed():
    """初始化随机数生成器的种子"""
    random.seed(time.time())


def get_uuid():
    """生成去除'-'的UUID字符串，并转换为大写"""
    return str(uuid.uuid4()).replace("-", "").upper()


def generate_key():
    """生成一个包含随机字符串和UUID的Token"""
    init_random_seed()  # 初始化随机种子
    key_part = "".join(
        random.choice(key_chars) for _ in range(16)
    )  # 生成16字符的随机字符串

    uuid_part = get_uuid()  # 获取UUID
    # 将UUID中的偶数位置的大写字母转换为小写（模仿Go代码的逻辑）
    uuid_processed = "".join(
        c.lower() if i % 2 == 0 else c for i, c in enumerate(uuid_part)
    )

    return key_part + uuid_processed  # 拼接并返回


def get_timestamp():
    """获取当前时间的时间戳"""
    return int(time.time())


def get_time_string():
    """获取当前时间的字符串表示，格式为年月日时分秒+纳秒"""
    now = time.localtime()
    return time.strftime("%Y%m%d%H%M%S", now) + str(time.time_ns() % 1e9)[:9]
