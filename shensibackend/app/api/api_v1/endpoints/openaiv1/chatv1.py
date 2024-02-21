import os
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from openai import AsyncOpenAI, OpenAIError as openai_error
router = APIRouter()
# api_key_oneapi = "sk-IjqBdKx2iuVNXKRxFbCbE2A9Cd284cE0A2Bd78036e095521"
os.environ["OPENAI_BASE_URL"] = "https://api.shensi.co/v1"
async def generate_stream(api_key, model, messages):
    try:
        async with AsyncOpenAI(api_key=api_key) as client:
            stream = await client.chat.completions.create(
                model=model, messages=messages, stream=True)
            async for chunk in stream:
                message_content = chunk.choices[0].delta.content or "\n"
                yield f"data: {message_content}\n\n"
            # 使用特定格式的结束信号
            yield "event: streaming-ended\n\n"
    except openai_error as e:
        error_message = f"OpenAI Error: {e}"
        yield f"data: {error_message}\n\n"
    except Exception as e:
        error_message = f"An error occurred: {e}"
        yield f"data: {error_message}\n\n"


@router.post("/chat_completions")
async def stream_chat(api_key: str, model: str, message: str):
    messages = [{"role": "user", "content": message}]

    # 创建StreamingResponse对象
    stream_response = StreamingResponse(
        generate_stream(api_key, model, messages),
        media_type="text/event-stream"
    )

    # 返回流式响应
    return stream_response