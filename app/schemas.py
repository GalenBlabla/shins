### 2. `schemas.py`
# 这个文件包含用于验证和序列化数据的 Pydantic 模型（schemas）。我们将创建用于用户注册、登录和更新密钥的模型。
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    username:str
    email: EmailStr
    phone_number: Optional[str] = None
    password: str
    verification_code: str


class UserLogin(BaseModel):
    login: str  # 可以是用户名、手机号或邮箱
    password: Optional[str] = None
    verification_code: Optional[str] = None

class KeyCreate(BaseModel):
    key: str

class KeyUpdate(BaseModel):
    key: str
    
class TokenData(BaseModel):
    username: str | None = None

class BindKeyRequest(BaseModel):
    key: str

class UserTokenData(BaseModel):
    user_id: int
    used_quota: int
    created_time: datetime
    expired_time: datetime
    status: int
    name: Optional[str]
    accessed_time: Optional[datetime]
    remain_quota: int
    unlimited_quota: bool

class UserPublicModel(BaseModel):
    id: int
    username: str
    email: str
    phone_number: str
    is_active: bool
    is_superuser: bool