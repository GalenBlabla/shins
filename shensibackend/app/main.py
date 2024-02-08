# FastAPI application main file.
import os
from dotenv import load_dotenv
from fastapi import FastAPI
from tortoise.contrib.fastapi import register_tortoise
from fastapi.middleware.cors import CORSMiddleware
from app.api.api_v1.endpoints import (
    user,
    item,
    token,
    keyserver,
)   # 导入您的路由
from app.api.api_v1.endpoints import alipayment
# from app.api.api_v1.admin import admin
from starlette.middleware.sessions import SessionMiddleware
from app.api.api_v1.admin.dashborad import dashboard
from app.api.api_v1.endpoints import captcha
load_dotenv()
app = FastAPI()
# 配置SessionMiddleware，设置密钥和会话cookie的名称
app.add_middleware(SessionMiddleware,
                   secret_key="your_secret_key", session_cookie="session")
# 示例路由


@app.get("/")
async def read_root():
    return {"Hello": "World"}

# 包含您的API路由
app.include_router(user.router)
app.include_router(item.router)
app.include_router(token.router)
app.include_router(keyserver.router)
app.include_router(captcha.router)
# app.include_router(admin.router)
app.include_router(dashboard.router)
app.include_router(alipayment.router)

# 添加 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有域的跨域请求，您可以根据需要更改为特定的域名
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有方法（GET, POST, PUT, DELETE 等）
    allow_headers=["*"],  # 允许所有头部
)
# Tortoise-ORM 配置
tortoise_config = {
    "connections": {
        "shensidb": f"mysql://{os.getenv('DB_SHENSI_USER')}:{os.getenv('DB_SHENSI_PASSWORD')}@{os.getenv('DB_SHENSI_HOST')}:{os.getenv('ShenSiDB_PORT')}/{os.getenv('DB_SHENSI_NAME')}",
        "oneapidb": f"mysql://{os.getenv('DB_ONEAPI_USER')}:{os.getenv('DB_ONEAPI_PASSWORD')}@{os.getenv('DB_ONEAPI_HOST')}:{os.getenv('oneapiDB_PORT')}/{os.getenv('DB_ONEAPI_NAME')}"
    },
    "apps": {
        "shensidb_app": {"models": ["app.models.shensimodels"], "default_connection": "shensidb"},
        "oneapidb_app": {"models": ["app.models.oneapimodels"], "default_connection": "oneapidb"},
    }
}

register_tortoise(
    app,
    config=tortoise_config,
    generate_schemas=True,
    add_exception_handlers=True
)

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app=app,host='0.0.0.0',port=8000)
