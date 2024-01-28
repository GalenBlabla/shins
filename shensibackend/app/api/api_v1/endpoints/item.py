# API endpoints for the 'item' resource.
from fastapi import APIRouter,HTTPException
from app.models import shensimodels, oneapimodels
router = APIRouter()

@router.get("/items/")
async def read_items():
    return {"items": "Here are your items"}

