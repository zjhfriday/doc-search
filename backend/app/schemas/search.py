"""
检索相关 Pydantic Schema
"""
from typing import Optional, List
from enum import Enum

from pydantic import BaseModel, Field


class SearchType(str, Enum):
    TEXT = "text"              # 文本/自然语言检索
    IMAGE = "image"            # 以图搜图
    FACE = "face"              # 人脸检索
    VIDEO_FRAME = "video_frame"  # 视频帧语义检索


class SearchRequest(BaseModel):
    """统一检索请求"""
    query: Optional[str] = Field(None, description="检索关键词或自然语言描述")
    search_type: SearchType = Field(SearchType.TEXT, description="检索类型")

    # 筛选条件
    material_type: Optional[str] = Field(None, description="素材类型: image/video")
    event_name: Optional[str] = Field(None, description="活动名称")
    date_from: Optional[str] = Field(None, description="开始日期 YYYY-MM-DD")
    date_to: Optional[str] = Field(None, description="结束日期 YYYY-MM-DD")
    person_name: Optional[str] = Field(None, description="人物姓名")
    scene: Optional[str] = Field(None, description="场景分类")
    min_quality: Optional[float] = Field(None, description="最低质量分(0-100)")
    security_level: Optional[str] = Field(None, description="密级过滤")
    exclude_duplicates: bool = Field(True, description="排除重复素材")

    # 分页
    page: int = Field(1, ge=1, description="页码")
    page_size: int = Field(20, ge=1, le=100, description="每页数量")


class SearchResultItem(BaseModel):
    """单条检索结果"""
    material_id: int
    filename: str
    material_type: str
    thumbnail_url: Optional[str] = None
    preview_url: Optional[str] = None
    relevance_score: float = Field(description="相关度分数")
    quality_score: Optional[float] = None
    security_level: str
    event_name: Optional[str] = None
    tags: List[str] = []
    matched_faces: List[str] = []
    # 视频专用
    timestamp_start: Optional[float] = Field(None, description="视频匹配起始时间(秒)")
    timestamp_end: Optional[float] = Field(None, description="视频匹配结束时间(秒)")
    created_at: Optional[str] = None


class SearchResponse(BaseModel):
    """检索响应"""
    total: int
    page: int
    page_size: int
    search_type: SearchType
    query: Optional[str] = None
    items: List[SearchResultItem]
