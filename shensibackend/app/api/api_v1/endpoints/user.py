# API endpoints for the 'user' resource.
from fastapi import APIRouter, HTTPException, Depends, Request
from passlib.context import CryptContext

from app.schemas.schemas import (
    PasswordUpdateModel,
    UserCreate,
    UserLogin,
    UserPublicModel,
)
from app.models.shensimodels import User_Pydantic, UserModel
from app.api.api_v1.dependencies import get_current_user
from app.services.user_services.user_service import (
    get_user_details,
    update_user_password,
    update_user_username,
)
from app.services.user_services.verification_service import (
    send_and_store_verification_code,
    # validate_captcha,
    clear_stored_verification_code,
)
from app.services.user_services.user_service import register_new_user
from app.services.user_services.auth_service import authenticate_and_generate_token
from app.services.utils.validate_verification_code import validate_verification_code

router = APIRouter(tags=["Users"])


@router.post("/users/send_verify_code")
async def send_verify_code(request: Request, mobile: str): #, captcha_input: str
    # if not validate_captcha(mobile, captcha_input):
    #     raise HTTPException(status_code=400, detail="Invalid CAPTCHA")
    try:
        await send_and_store_verification_code(mobile)

        return {"message": "Verification code sent successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/users/me", response_model=UserPublicModel)
async def read_users_me(current_user: UserModel = Depends(get_current_user)):
    user_details = await get_user_details(current_user.id)
    return user_details


# @router.post("/users/register", response_model=User_Pydantic)
# async def register_user(user: UserCreate, verification_code: str):
#     is_code_valid = await validate_verification_code(
#         user.phone_number, verification_code
#     )
#     if not is_code_valid:
#         raise HTTPException(
#             status_code=400, detail="Invalid or expired verification code"
#         )

#     try:
#         db_user = await register_new_user(user)
#         clear_stored_verification_code(user.phone_number)
#         return await User_Pydantic.from_tortoise_orm(db_user)
#     except ValueError as e:
#         raise HTTPException(status_code=400, detail=str(e))


# @router.post("/users/login")
# async def login_for_access_token(form_data: UserLogin,verification_code: str):
#     is_code_valid = await validate_verification_code(
#         form_data.phone_number, verification_code
#     )
#     if not is_code_valid:
#         raise HTTPException(
#             status_code=400, detail="Invalid or expired verification code"
#         )
#     token = await authenticate_and_generate_token(
#         login=form_data.phone_number,
#         password=None,
#         verification_code=verification_code,
#     )
#     return token
async def authenticate_or_register(user: UserCreate):
    # 检查用户是否存在
    existing_user = await UserModel.get_or_none(phone_number=user.phone_number)
    if existing_user:
        # 用户已存在，进行登录流程
        token = await authenticate_and_generate_token(
            login=user.phone_number,
        )
        return token, None
    else:
        # 用户不存在，进行注册流程
        db_user = await register_new_user(user)
        token = await authenticate_and_generate_token(
            login=user.phone_number,
        )
        return token, db_user
@router.post("/users/auth")
async def register_or_login(user: UserCreate, verification_code: str):
    print(user.phone_number, verification_code)
    is_code_valid = await validate_verification_code(
        user.phone_number, verification_code
    )
    if not is_code_valid:
        raise HTTPException(
            status_code=400, detail="Invalid or expired verification code"
        )

    # 尝试检查用户是否已经存在并进行登录，如果不存在则注册
    token, db_user = await authenticate_or_register(user)

    # 清除存储的验证码
    clear_stored_verification_code(user.phone_number)

    # 如果用户是新注册的，可以返回用户的信息
    if db_user:
        user_info = await User_Pydantic.from_tortoise_orm(db_user)
        return {"token": token, "user": user_info}
    else:
        return {"token": token}
    

@router.put("/users/change_username")
async def update_username(
    new_username: str, current_user: UserModel = Depends(get_current_user)
):
    message = await update_user_username(current_user, new_username)
    return {"message": message}


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@router.put("/users/update-password")
async def update_password(
    password_update: PasswordUpdateModel,
    current_user: UserModel = Depends(get_current_user),
):
    message = await update_user_password(
        current_user, password_update.old_password, password_update.new_password
    )
    return {"message": message}
