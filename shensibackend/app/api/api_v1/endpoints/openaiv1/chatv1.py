import os
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from dotenv import load_dotenv
from openai import OpenAI

from app.services.openai_services.chat_services import generate_stream
from app.schemas.schemas import ChatRequest
from app.api.api_v1.dependencies import get_current_user
from app.models.shensimodels import UserModel,KeyModel

load_dotenv()


router = APIRouter()

# api_key_oneapi = "sk-IjqBdKx2iuVNXKRxFbCbE2A9Cd284cE0A2Bd78036e095521"
os.environ["OPENAI_BASE_URL"] = os.getenv("OPENAI_BASE_URL","http://34.80.104.111:3000/v1")


@router.get("/chat_completions")
async def stream_chat(request:ChatRequest,current_user: UserModel = Depends(get_current_user)):
    # 从数据库中查找与当前用户相关联的 API 密钥
    user_key = await KeyModel.filter(user=current_user.id, is_active=True).first()
    if not user_key:
        raise HTTPException(status_code=404, detail="Active API key not found for the user")
    # 创建StreamingResponse对象
    stream_response = StreamingResponse(
        generate_stream(api_key='sk-'+user_key.key, model=request.model, messages=request.messages),
        media_type="text/event-stream"
    )

    # 返回流式响应
    return stream_response

@router.post("/chat_completion_full")
async def chat_no_stream(request: ChatRequest,current_user: UserModel = Depends(get_current_user)):
    try:
        # 从数据库中查找与当前用户相关联的 API 密钥
        user_key = await KeyModel.filter(user=current_user.id, is_active=True).first()
        if not user_key:
            raise HTTPException(status_code=404, detail="Active API key not found for the user")
        # 初始化 OpenAI 客户端（替换 YOUR_API_KEY 为你的 OpenAI API 密钥）
        client = OpenAI(api_key='sk-'+user_key.key)
        # 转换消息格式
        formatted_messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]

        # 调用 OpenAI 完成对话
        response = client.chat.completions.create(
            model=request.model,
            messages=formatted_messages
        )

        # 返回响应
        return {"response": response.choices[0].message}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
