from fastapi import HTTPException, status
from datetime import timedelta
from app.models.shensimodels import UserModel
from app.crud import authenticate_user
from app.dependencies import create_access_token

from app.dependencies import ACCESS_TOKEN_EXPIRE_MINUTES
from app.services.utils.validate_verification_code import validate_verification_code

async def authenticate_and_generate_token(login: str, password: str = None, verification_code: str = None) -> dict:
    user = None
    if password:
        user = await authenticate_user(login, password)
    elif verification_code:
        is_code_valid = await validate_verification_code(login, verification_code)
        if is_code_valid:
            user = await UserModel.get_or_none(phone_number=login) or await UserModel.get_or_none(email=login)
        else:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid verification code")
    
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect login details")

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = await create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)
    
    return {"access_token": access_token, "token_type": "bearer"}
