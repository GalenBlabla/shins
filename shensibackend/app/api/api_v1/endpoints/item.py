# API endpoints for the 'item' resource.
from fastapi import APIRouter

router = APIRouter()


@router.get("/items/")
async def read_items():
    return {"items": "Here are your items"}
