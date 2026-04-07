"""
用户相关 Pydantic Schema
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.models.user import RoleEnum


# ── 请求 ─────────────────────────────────────────────────────────

class UserCreate(BaseModel):
    username: str = Field(..., min_length=2, max_length=50, description="用户名")
    password: str = Field(..., min_length=6, max_length=100, description="密码")
    display_name: Optional[str] = Field(None, max_length=100, description="显示名称")
    email: Optional[str] = None
    department: Optional[str] = None
    role: RoleEnum = RoleEnum.USER


class UserUpdate(BaseModel):
    display_name: Optional[str] = None
    email: Optional[str] = None
    department: Optional[str] = None
    role: Optional[RoleEnum] = None
    is_active: Optional[bool] = None


class LoginRequest(BaseModel):
    username: str
    password: str


# ── 响应 ─────────────────────────────────────────────────────────

class UserResponse(BaseModel):
    id: int
    username: str
    display_name: Optional[str] = None
    email: Optional[str] = None
    department: Optional[str] = None
    role: RoleEnum
    is_active: bool
    last_login_at: Optional[datetime] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
