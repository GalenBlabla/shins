from fastapi import APIRouter
from typing import List
from typing import List, Optional
from fastapi import APIRouter, Query
from app.schemas import UserPublicModel
from app.models.shensimodels import UserModel

router = APIRouter()


router = APIRouter()


@router.get("/users/", response_model=List[UserPublicModel])
async def list_users():
    """
    List all users.
    """
    users = await UserModel.all()
    return [UserPublicModel(
        id=user.id,
        username=user.username,
        email=user.email,
        phone_number=user.phone_number,
        is_active=user.is_active,
        is_superuser=user.is_superuser
        ) for user in users]
