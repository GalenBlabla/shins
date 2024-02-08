import os
import logging

from alipay.aop.api.DefaultAlipayClient import DefaultAlipayClient
from alipay.aop.api.domain.AlipayTradePagePayModel import AlipayTradePagePayModel
from alipay.aop.api.request.AlipayTradePagePayRequest import AlipayTradePagePayRequest
from alipay.aop.api.AlipayClientConfig import AlipayClientConfig
from app.models.shensimodels import OrderModel
from tortoise.transactions import in_transaction


from app.models.shensimodels import KeyModel, OrderModel
from app.models.oneapimodels import Tokens
from app.services.utils.alipay.generate_order_number import generate_order_number
from app.services.utils.alipay.verify_alipay_signature import verify_alipay_signature


alipay_client_config = AlipayClientConfig()
alipay_client_config.server_url = 'https://openapi-sandbox.dl.alipaydev.com/gateway.do'
alipay_client_config.app_id = os.getenv("APP_ID")
alipay_client_config.app_private_key = os.getenv("APP_PRIVATE_KEY")
alipay_client_config.alipay_public_key = os.getenv("ALIPAY_PUBLIC_KEY")

async def initiate_payment(user_id: int, total_amount: float, subject: str, body: str) -> str:
    out_trade_no = generate_order_number(user_id)
    async with in_transaction("shensidb") as conn:
        await OrderModel.create(
            user_id=user_id,
            out_trade_no=out_trade_no,
            total_amount=total_amount,
            subject=subject,
            body=body,
            status="PENDING"
        )

    client = DefaultAlipayClient(alipay_client_config=alipay_client_config)
    model = AlipayTradePagePayModel()
    model.out_trade_no = out_trade_no
    model.total_amount = str(total_amount)
    model.subject = subject
    model.body = body
    model.product_code = "FAST_INSTANT_TRADE_PAY"

    pay_request = AlipayTradePagePayRequest(biz_model=model)
    pay_request.return_url = os.getenv("ALIPAY_RETURN_URL")
    pay_request.notify_url = os.getenv("ALIPAY_NOTIFY_URL")
    response = client.page_execute(pay_request, http_method="GET")
    
    return response



logger = logging.getLogger(__name__)
# 假设已在文件开头或配置模块中定义
QUOTA_MULTIPLIER = int(os.getenv("QUOTA", "70000"))

async def process_payment_notification(data_dict: dict):
    if not verify_alipay_signature(data_dict):
        logger.error("Invalid payment signature")
        raise ValueError("Invalid signature")

    out_trade_no = data_dict.get('out_trade_no')
    async with in_transaction('shensidb') as conn:
        order = await OrderModel.get_or_none(out_trade_no=out_trade_no).using_db(conn)
        if not order or order.status == "COMPLETED":
            return "success"

        if data_dict.get('trade_status') == "TRADE_SUCCESS":
            order.status = "COMPLETED"
            await order.save(using_db=conn)
            logger.info(f"Order status updated to COMPLETED: {out_trade_no}")

            keys = await KeyModel.filter(user_id=order.user_id).values_list('key', flat=True)
            for api_key in keys:
                token = await Tokens.get_or_none(key=api_key)
                if token:
                    token.remain_quota += order.total_amount * QUOTA_MULTIPLIER
                    await token.save()

    return "success"
