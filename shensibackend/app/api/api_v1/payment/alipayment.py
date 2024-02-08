from fastapi import APIRouter, Depends
from app.dependencies import get_current_user
from fastapi import APIRouter, Request, Depends
from app.models.shensimodels import UserModel
from app.dependencies import get_current_user
from app.services.payment_service import initiate_payment, process_payment_notification

router = APIRouter(tags=["AliPayment"])

@router.post('/pay')
async def pay(total_amount: float, subject: str, body: str, current_user: UserModel = Depends(get_current_user)):
    response = await initiate_payment(current_user.id, total_amount, subject, body)
    return {"url": response}

@router.post("/payment/notify")
async def payment_notify(request: Request):
    data_dict = dict(await request.form())
    result = await process_payment_notification(data_dict)
    return result
