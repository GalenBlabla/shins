from fastapi import APIRouter, Depends, Request
from app.api.api_v1.dependencies import get_current_user
from app.models.shensimodels import UserModel
from app.services.user_services.payment_service import (
    initiate_payment,
    process_payment_notification,
)
from app.schemas.schemas import PaymentInfo

router = APIRouter(tags=["AliPayment"])


@router.post("/payment/alipay")
async def pay(
    payment_info: PaymentInfo, current_user: UserModel = Depends(get_current_user)
):
    """
    device_type: pc or phone
    """
    response = await initiate_payment(
        current_user.id,
        payment_info.total_amount,
        payment_info.subject,
        payment_info.body,
        payment_info.device_type,
    )
    return {"url": response}


@router.post("/payment/notify")
async def payment_notify(request: Request):
    data_dict = dict(await request.form())
    result = await process_payment_notification(data_dict)
    return result
