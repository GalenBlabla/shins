from fastapi import HTTPException, status
from datetime import timedelta
from app.models.shensimodels import UserModel
from app.api.api_v1.dependencies import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    create_access_token,
)
async def authenticate_and_generate_token(
    login: str
) -> dict:
    user = None
    user = await UserModel.get_or_none(
                phone_number=login
            )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect login details"
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = await create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}
