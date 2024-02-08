from datetime import datetime
import os
import random
from dotenv import load_dotenv
import logging

from fastapi import APIRouter, Depends
from alipay.aop.api.DefaultAlipayClient import DefaultAlipayClient
from alipay.aop.api.domain.AlipayTradePagePayModel import AlipayTradePagePayModel
from alipay.aop.api.request.AlipayTradePagePayRequest import AlipayTradePagePayRequest
from alipay.aop.api.AlipayClientConfig import AlipayClientConfig
from app.payment.utils.generate_order_number import generate_order_number
from app.payment.utils.verify_alipay_signature import verify_alipay_signature
from tortoise.transactions import in_transaction


from app.dependencies import get_current_user
from app.models.shensimodels import KeyModel, OrderModel, UserModel
from fastapi import APIRouter, HTTPException, Request, Depends
from alipay.aop.api.response.AlipayTradePagePayResponse import AlipayTradePagePayResponse
from app.models.shensimodels import OrderModel, UserModel
from app.dependencies import get_current_user
import json

from app.models.oneapimodels import Tokens

load_dotenv()

# 配置支付宝客户端
alipay_client_config = AlipayClientConfig()
alipay_client_config.server_url = 'https://openapi-sandbox.dl.alipaydev.com/gateway.do'
alipay_client_config.app_id = os.getenv("APP_ID")
alipay_client_config.app_private_key = os.getenv("APP_PRIVATE_KEY")
alipay_client_config.alipay_public_key = os.getenv("ALIPAY_PUBLIC_KEY")

router = APIRouter()


def generate_order_number(user_id: int) -> str:
    date_str = datetime.now().strftime("%Y%m%d%H%M%S")
    random_str = str(random.randint(1000, 9999))
    return f"ORD{date_str}{user_id}{random_str}"


@router.post('/pay')
async def pay(
        total_amount: float,
        subject: str,
        body: str,
        current_user: UserModel = Depends(get_current_user)):

    out_trade_no = generate_order_number(current_user.id)
    connection_name = "shensidb" 
    async with in_transaction(connection_name=connection_name) as conn:
        order = await OrderModel.create(
            user_id=current_user.id,
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
    # 或使用 settings.ALIPAY_RETURN_URL
    pay_request.return_url = os.getenv("ALIPAY_RETURN_URL")
    # 或使用 settings.ALIPAY_NOTIFY_URL
    pay_request.notify_url = os.getenv("ALIPAY_NOTIFY_URL")
    # 如果http_method是GET，则是一个带完成请求参数的url，如果http_method是POST，则是一段HTML表单片段
    response = client.page_execute(pay_request, http_method="GET")
    # 可以根据需要返回完整的URL或HTML表单片段
    return {"url": response}




# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
@router.post("/payment/notify")
async def payment_notify(request: Request):
    """
    支付宝支付结果通知接口。
    当支付宝支付成功后，支付宝会向该接口发送通知。

    步骤:
    1. 解析请求体中的数据。
    2. 验证通知数据的签名确保数据的真实性。
    3. 检查订单状态，避免重复处理。
    4. 更新订单状态和用户余额。
    5. 返回成功响应给支付宝。
    """
    # 解析支付宝发送的通知数据
    data = await request.form()
    data_dict = dict(data)
    logger.info(f"Received Alipay notification: {data_dict}")

    # 验证通知数据的签名确保数据的真实性
    if not verify_alipay_signature(data_dict):
        logger.error("Invalid signature in Alipay notification.")
        raise HTTPException(status_code=400, detail="Invalid signature")

    # 检查订单状态，避免重复处理
    out_trade_no = data_dict.get('out_trade_no')
    async with in_transaction('shensidb') as conn:
        order = await OrderModel.get_or_none(out_trade_no=out_trade_no).using_db(conn)
        logger.info(f"Order: {order}")
        if not order:
            # 如果订单不存在
            logger.warning(f"Order not found: {out_trade_no}")
            raise HTTPException(status_code=404, detail="Order not found")
        elif order.status == "COMPLETED":
            # 如果订单已处理，则返回成功响应给支付宝
            logger.info(f"Order already completed: {out_trade_no}")
            return "success"

        # 更新订单状态和用户余额
        if data_dict.get('trade_status') == "TRADE_SUCCESS":
            logger.info(f"Updating order and user balance for: {out_trade_no}")
            order.status = "COMPLETED"
            await order.save(using_db=conn)
            '''
            先存储订单
            根据订单信息找到该用户
            找到该用户的token key
            为对应的key 加上余额
            '''
            # 在KeyModel中找到用户的API Key
            keys = await KeyModel.filter(user_id=order.user_id).all().values()
            for key in keys:
                logger.info(f"User ID: {key['user_id']}, Key: {key['key']}")
                token = await Tokens.get_or_none(key=keys)
                logger.info(f"Order—userid already completed: {order.user_id}")
                user = await Tokens.get(id=order.user_id)
                user.remain_quota += (order.total_amount * int(os.getenv("QUOTA")))  # 假设 UserModel 有一个余额字段
                await user.save()

    logger.info("Alipay notification processed successfully.")
    # 返回成功响应给支付宝
    return "success"