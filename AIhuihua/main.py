import asyncio
import datetime
import json
import random
import uuid
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from aiofiles import open as aio_open
from image_processor import ImageProcessor
from config import config
import pika

app = FastAPI()

# 允许的跨域源列表
origins = [
    "http://localhost:3000",  # 假设你的前端运行在3000端口
    "https://localhost:3000",
    "http://localhost:8080",
    "http://localhost:8000",  # 允许FastAPI的Swagger UI访问
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 服务静态文件
app.mount("/static", StaticFiles(directory="static"), name="static")

# 确保上传目录存在
UPLOAD_DIR = Path("./uploaded_images")
UPLOAD_DIR.mkdir(exist_ok=True)

image_processor = ImageProcessor(config["base_url"], config.get("proxy_url"))

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_bytes()
            # 生成文件名
            file_path = UPLOAD_DIR / f"image_{datetime.datetime.now().isoformat()}.png"
            # 异步写入文件
            async with aio_open(file_path, 'wb') as f:
                await f.write(data)
            print(f"Saved image to {file_path}")

            # 处理图片
            processed_image = await process_image(file_path)
            await websocket.send_bytes(processed_image)
    except WebSocketDisconnect:
        print("Client disconnected.")

async def process_image(file_path):
    # 上传图片到服务器
    image_name_server = image_processor.upload_image(file_path)

    # 准备prompt workflow
    with open(Path('static/workflow_api_huihua_2_1.json'), 'r') as file:
        prompt_workflow = json.load(file)

    # 设置prompt workflow
    prompt_workflow["13"]["inputs"]["image"] = f"/workspace/ComfyUI/input/{image_name_server}"
    prompt_workflow["3"]["inputs"]["denoise"] = 1.0
    prompt_workflow["3"]["inputs"]["seed"] = random.randint(0, 4284967295) * random.randint(0, 10000)
    prompt_workflow["6"]["inputs"]["text"] = "猫"
    prompt_workflow["29"]["inputs"]["width"] = 618
    prompt_workflow["29"]["inputs"]["height"] = 884

    # 队列prompt
    prompt_id = image_processor.queue_prompt(prompt_workflow)
    if not prompt_id:
        return None

    # 生成 UUID 并发送到队列
    uuid_value = str(uuid.uuid4())
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='uuid_queue')
    channel.basic_publish(exchange='', routing_key='uuid_queue', body=uuid_value)
    connection.close()

    # 等待处理完成信号
    image_processor.wait_for_image_processed_signal()

    images = image_processor.get_images()
    if images:
        return images[0]
    return None
