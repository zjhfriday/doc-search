"""
素材相关 Pydantic Schema
"""
from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field

from app.models.material import (
    MaterialType, MaterialStatus, SecurityLevel, TagCategory,
)


# ── 标签 ─────────────────────────────────────────────────────────

class TagBase(BaseModel):
    name: str
    category: TagCategory = TagCategory.KEYWORD


class TagResponse(TagBase):
    id: int
    model_config = {"from_attributes": True}


# ── 人脸 ─────────────────────────────────────────────────────────

class FaceInMaterial(BaseModel):
    id: int
    person_name: Optional[str] = None
    confidence: Optional[float] = None
    expression: Optional[str] = None
    bbox_x: Optional[int] = None
    bbox_y: Optional[int] = None
    bbox_w: Optional[int] = None
    bbox_h: Optional[int] = None
    model_config = {"from_attributes": True}


# ── 素材上传请求 ─────────────────────────────────────────────────

class MaterialUploadMeta(BaseModel):
    """上传素材时的附加信息"""
    event_name: Optional[str] = Field(None, max_length=300, description="活动名称")
    event_date: Optional[datetime] = Field(None, description="活动日期")
    security_level: SecurityLevel = Field(SecurityLevel.INTERNAL, description="密级")
    description: Optional[str] = Field(None, description="素材描述")
    tags: Optional[List[str]] = Field(default_factory=list, description="手动标签")


# ── 素材响应 ─────────────────────────────────────────────────────

class MaterialResponse(BaseModel):
    id: int
    filename: str
    material_type: MaterialType
    file_size: int
    thumbnail_path: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    duration: Optional[float] = None
    title: Optional[str] = None
    description: Optional[str] = None
    event_name: Optional[str] = None
    event_date: Optional[datetime] = None
    status: MaterialStatus
    security_level: SecurityLevel
    quality_score: Optional[float] = None
    is_duplicate: bool = False
    ocr_text: Optional[str] = None
    asr_text: Optional[str] = None
    tags: List[TagResponse] = []
    faces: List[FaceInMaterial] = []
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class MaterialListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: List[MaterialResponse]


# ── 素材更新 ─────────────────────────────────────────────────────

class MaterialUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    event_name: Optional[str] = None
    event_date: Optional[datetime] = None
    security_level: Optional[SecurityLevel] = None
    status: Optional[MaterialStatus] = None
    tags: Optional[List[str]] = None
