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
    validate_captcha,
    clear_stored_verification_code,
)
from app.services.user_services.user_service import register_new_user
from app.services.user_services.auth_service import authenticate_and_generate_token
from app.services.utils.validate_verification_code import validate_verification_code

router = APIRouter(tags=["Users"])


@router.post("/users/send_verify_code")
async def send_verify_code(request: Request, mobile: str, captcha_input: str):
    if not validate_captcha(mobile, captcha_input):
        raise HTTPException(status_code=400, detail="Invalid CAPTCHA")
    try:
        await send_and_store_verification_code(mobile)

        return {"message": "Verification code sent successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/users/me", response_model=UserPublicModel)
async def read_users_me(current_user: UserModel = Depends(get_current_user)):
    user_details = await get_user_details(current_user.id)
    return user_details


@router.post("/users/register", response_model=User_Pydantic)
async def register_user(user: UserCreate, verification_code: str):
    is_code_valid = await validate_verification_code(
        user.phone_number, verification_code
    )
    if not is_code_valid:
        raise HTTPException(
            status_code=400, detail="Invalid or expired verification code"
        )

    try:
        db_user = await register_new_user(user)
        clear_stored_verification_code(user.phone_number)
        return await User_Pydantic.from_tortoise_orm(db_user)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/users/login")
async def login_for_access_token(form_data: UserLogin):
    token = await authenticate_and_generate_token(
        form_data.login,
        password=form_data.password,
        verification_code=form_data.verification_code,
    )
    return token


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
