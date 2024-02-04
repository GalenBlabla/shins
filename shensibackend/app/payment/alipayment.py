from datetime import datetime
import os
import random
from dotenv import load_dotenv

from fastapi import APIRouter, Depends
from alipay.aop.api.DefaultAlipayClient import DefaultAlipayClient
from alipay.aop.api.domain.AlipayTradePagePayModel import AlipayTradePagePayModel
from alipay.aop.api.request.AlipayTradePagePayRequest import AlipayTradePagePayRequest
from alipay.aop.api.AlipayClientConfig import AlipayClientConfig
from app.payment.utils.generate_order_number import generate_order_number
from tortoise.transactions import in_transaction

from app.dependencies import get_current_user
from app.models.shensimodels import OrderModel, UserModel

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
