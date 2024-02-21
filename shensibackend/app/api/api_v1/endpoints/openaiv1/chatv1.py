import os
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from dotenv import load_dotenv

from app.services.openai_services.chat_services import generate_stream
from app.schemas.schemas import ChatRequest
from app.api.api_v1.dependencies import get_current_user
from app.models.shensimodels import UserModel,KeyModel

load_dotenv()


router = APIRouter()

# api_key_oneapi = "sk-IjqBdKx2iuVNXKRxFbCbE2A9Cd284cE0A2Bd78036e095521"
os.environ["OPENAI_BASE_URL"] = os.getenv("OPENAI_BASE_URL","http://34.80.104.111:3000/v1")


@router.post("/chat_completions")
async def stream_chat(request:ChatRequest,current_user: UserModel = Depends(get_current_user)):
    # 从数据库中查找与当前用户相关联的 API 密钥
    user_key = await KeyModel.filter(user=current_user.id, is_active=True).first()
    print(user_key.key)
    if not user_key:
        raise HTTPException(status_code=404, detail="Active API key not found for the user")
    # 创建StreamingResponse对象
    stream_response = StreamingResponse(
        generate_stream(api_key='sk-'+user_key, model=request.model, messages=request.messages),
        media_type="text/event-stream"
    )

    # 返回流式响应
    return stream_response