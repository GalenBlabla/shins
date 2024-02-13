import os
from urllib.parse import quote_plus
from collections import OrderedDict
from dotenv import load_dotenv

load_dotenv()


# 以下是辅助函数，用于验证支付宝的签名
def verify_alipay_signature(data):
    """
    验证支付宝发送的通知数据的签名。

    参数:
    - data (dict): 支付宝发送的通知数据。

    返回:
    - bool: 签名是否有效。
    """
    # 此处应实现签名验证逻辑，确保数据未被篡改
    # 示例代码中省略了实现细节
    # 解析支付宝发送的通知数据
    return True
