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
async def pay(total_amount: float,subject: str,body: str,current_user: UserModel = Depends(get_current_user)):

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
    pay_request.return_url = os.getenv("ALIPAY_RETURN_URL")
    pay_request.notify_url = os.getenv("ALIPAY_NOTIFY_URL")
    # 如果http_method是GET，则是一个带完成请求参数的url，如果http_method是POST，则是一段HTML表单片段
    response = client.page_execute(pay_request, http_method="GET")
    # 可以根据需要返回完整的URL或HTML表单片段
    return {"url": response}


# 假设已在文件开头或配置模块中定义
QUOTA_MULTIPLIER = int(os.getenv("QUOTA", "100"))
async def verify_payment_signature(data_dict):
    if not verify_alipay_signature(data_dict):
        logger.error("Invalid payment signature")
        raise HTTPException(status_code=400, detail="Invalid signature")

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
async def payment_notify(request: Request):
    data = await request.form()
    data_dict = dict(data)
    
    # 验证签名
    await verify_payment_signature(data_dict)

    out_trade_no = data_dict.get('out_trade_no')
    async with in_transaction('shensidb') as conn:
        order = await OrderModel.get_or_none(out_trade_no=out_trade_no).using_db(conn)
        if not order:
            logger.warning(f"Order not found: {out_trade_no}")
            raise HTTPException(status_code=404, detail="Order not found")
        if order.status == "COMPLETED":
            logger.info(f"Order already completed: {out_trade_no}")
            return "success"

        if data_dict.get('trade_status') == "TRADE_SUCCESS":
            order.status = "COMPLETED"
            await order.save(using_db=conn)
            logger.info(f"Order status updated to COMPLETED: {out_trade_no}")

            keys = await KeyModel.filter(user_id=order.user_id).values_list('key', flat=True)
            for api_key in keys:
                logger.info(f"Processing token for Key: {api_key}")
                token = await Tokens.get_or_none(key=api_key)
                if token:
                    token.remain_quota += order.total_amount * QUOTA_MULTIPLIER
                    await token.save()
                    logger.info(f"Token balance updated for Key: {api_key}")

    return "success"