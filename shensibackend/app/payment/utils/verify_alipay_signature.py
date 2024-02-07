import os
from urllib.parse import quote_plus
from collections import OrderedDict
from alipay.aop.api.util.SignatureUtils import *
from dotenv import load_dotenv
from fastapi import HTTPException

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
    data_dict = dict(data)
    # 提取签名
    sign = data_dict.pop('sign', None)
    # 忽略空值和签名类型，构造待验签的内容
    ordered_data = OrderedDict(sorted(data_dict.items()))
    message = "&".join(f"{k}={quote_plus(v)}" for k, v in ordered_data.items() if v != '')

    # 验证通知数据的签名确保数据的真实性
    public_key = os.getenv("ALIPAY_PUBLIC_KEY")  # 替换为您的支付宝公钥
    if not verify_with_rsa(public_key, message, sign):
        raise HTTPException(status_code=400, detail="Invalid signature")
    return True