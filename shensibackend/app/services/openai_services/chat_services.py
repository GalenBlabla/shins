from openai import AsyncOpenAI, OpenAIError as openai_error

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
