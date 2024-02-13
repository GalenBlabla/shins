import os
import logging
from dotenv import load_dotenv

from alipay.aop.api.DefaultAlipayClient import DefaultAlipayClient
from alipay.aop.api.domain.AlipayTradePagePayModel import AlipayTradePagePayModel
from alipay.aop.api.request.AlipayTradePagePayRequest import AlipayTradePagePayRequest
from alipay.aop.api.AlipayClientConfig import AlipayClientConfig
from tortoise.transactions import in_transaction

# shoujizhifu
from alipay.aop.api.domain.AlipayTradeWapPayModel import AlipayTradeWapPayModel
from alipay.aop.api.request.AlipayTradeWapPayRequest import AlipayTradeWapPayRequest


from app.models.shensimodels import KeyModel, OrderModel
from app.models.oneapimodels import Tokens
from app.services.utils.alipay.generate_order_number import generate_order_number
from app.services.utils.alipay.verify_alipay_signature import verify_alipay_signature

load_dotenv()
# 配置日志
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)


def load_private_key_from_file(private_key_path):
    """
    从文件中加载私钥。

    :param private_key_path: 私钥文件的路径
    :return: 私钥字符串
    """
    try:
        with open(private_key_path, "r") as file:
            private_key = file.read()
        return private_key
    except Exception as e:
        return None


def load_public_key_from_file(public_key_path):
    """
    从文件中加载公钥。

    :param public_key_path: 公钥文件的路径
    :return: 公钥字符串
    """
    try:
        with open(public_key_path, "r") as file:
            public_key = file.read()
        return public_key
    except Exception:
        return None


# 初始化支付宝客户端配置
def init_alipay_client():
    alipay_client_config = AlipayClientConfig()
    alipay_client_config.server_url = os.getenv("SERVER_URL")
    alipay_client_config.app_id = os.getenv("APP_ID")
    alipay_client_config.app_private_key = load_private_key_from_file(
        os.getenv("PRIVATE_KEY_PATH")
    )
    alipay_client_config.alipay_public_key = load_public_key_from_file(
        os.getenv("PUBLIC_KEY_PATH")
    )
    return DefaultAlipayClient(alipay_client_config=alipay_client_config)


# 创建并发送支付请求
async def create_and_send_payment_request(client, model, return_url, notify_url):
    if isinstance(model, AlipayTradeWapPayModel):
        pay_request = AlipayTradeWapPayRequest()
    else:
        pay_request = AlipayTradePagePayRequest()

    pay_request.biz_model = model
    pay_request.return_url = return_url
    pay_request.notify_url = notify_url

    logger.info("Sending payment request to Alipay...")
    response = client.page_execute(pay_request, http_method="GET")
    logger.info(f"Received response from Alipay: {response}")
    return response


# 封装支付初始化逻辑
async def initiate_payment(
    user_id: int, total_amount: float, subject: str, body: str, device_type: str
) -> str:
    out_trade_no = generate_order_number(user_id)
    await save_order_to_db(user_id, out_trade_no, total_amount, subject, body)

    client = init_alipay_client()

    if device_type.lower() == "phone":
        model = AlipayTradeWapPayModel()
        model.product_code = "QUICK_WAP_WAY"
    else:
        model = AlipayTradePagePayModel()
        model.product_code = "FAST_INSTANT_TRADE_PAY"

    model.out_trade_no = out_trade_no
    model.total_amount = str(total_amount)
    model.subject = subject
    model.body = body

    return_url = os.getenv("ALIPAY_RETURN_URL")
    notify_url = os.getenv("ALIPAY_NOTIFY_URL")

    return await create_and_send_payment_request(client, model, return_url, notify_url)


# 保存订单到数据库
async def save_order_to_db(user_id, out_trade_no, total_amount, subject, body):
    async with in_transaction("shensidb"):
        await OrderModel.create(
            user_id=user_id,
            out_trade_no=out_trade_no,
            total_amount=total_amount,
            subject=subject,
            body=body,
            status="PENDING",
        )
        logger.info("Order saved to database with status PENDING.")


# 假设已在文件开头或配置模块中定义
QUOTA_MULTIPLIER = int(os.getenv("QUOTA", "70000"))


async def process_payment_notification(data_dict: dict):
    logger.info("Processing payment notification...")

    if not verify_alipay_signature(data_dict):
        logger.error("Invalid payment signature")
        raise ValueError("Invalid signature")

    out_trade_no = data_dict.get("out_trade_no")
    logger.info(f"Processing order: {out_trade_no}")

    async with in_transaction("shensidb") as conn:
        order = await OrderModel.get_or_none(out_trade_no=out_trade_no).using_db(conn)
        if not order:
            logger.error(f"Order not found: {out_trade_no}")
            return "success"
        elif order.status == "COMPLETED":
            logger.info(f"Order already completed: {out_trade_no}")
            return "success"

        if data_dict.get("trade_status") == "TRADE_SUCCESS":
            order.status = "COMPLETED"
            await order.save(using_db=conn)
            logger.info(f"Order status updated to COMPLETED: {out_trade_no}")

            keys = await KeyModel.filter(user_id=order.user_id).values_list(
                "key", flat=True
            )
            for api_key in keys:
                token = await Tokens.get_or_none(key=api_key)
                if token:
                    token.remain_quota += order.total_amount * QUOTA_MULTIPLIER
                    await token.save()
                    logger.info(f"Quota updated for token: {api_key}")

    return "success"
