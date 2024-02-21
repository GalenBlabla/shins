import os
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from dotenv import load_dotenv

from app.services.openai_services.chat_services import generate_stream
from app.schemas.schemas import ChatRequest

load_dotenv()


router = APIRouter()

# api_key_oneapi = "sk-IjqBdKx2iuVNXKRxFbCbE2A9Cd284cE0A2Bd78036e095521"
os.environ["OPENAI_BASE_URL"] = os.getenv("OPENAI_BASE_URL","https://api.shensi.co/v1")


@router.get("/chat_completions")
async def stream_chat(request:ChatRequest):
    messages = [{"role": "user", "content": request.message}]

    # 创建StreamingResponse对象
    stream_response = StreamingResponse(
        generate_stream(request.api_key, request.model, messages),
        media_type="text/event-stream"
    )

    # 返回流式响应
    return stream_response