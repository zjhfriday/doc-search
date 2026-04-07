"""
素材、标签、人脸 模型
"""
import enum
from datetime import datetime, timezone

from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime, Enum,
    ForeignKey, Text, BigInteger, Table,
)
from sqlalchemy.orm import relationship

from app.core.database import Base


# ── 枚举 ────────────────────────────────────────────────────────

class MaterialType(str, enum.Enum):
    IMAGE = "image"
    VIDEO = "video"


class MaterialStatus(str, enum.Enum):
    PENDING = "pending"           # 待审核
    PROCESSING = "processing"     # AI处理中
    APPROVED = "approved"         # 已通过
    REJECTED = "rejected"         # 已驳回
    ARCHIVED = "archived"         # 已归档


class SecurityLevel(str, enum.Enum):
    PUBLIC = "public"             # 公开
    INTERNAL = "internal"         # 内部
    RESTRICTED = "restricted"     # 受限（需审批下载）
    CONFIDENTIAL = "confidential" # 涉密


class TagCategory(str, enum.Enum):
    PERSON = "person"             # 人物
    SCENE = "scene"               # 场景
    EVENT = "event"               # 活动
    KEYWORD = "keyword"           # 关键词
    AI_GENERATED = "ai_generated" # AI生成标签


# ── 多对多关联表 ─────────────────────────────────────────────────

material_tag_table = Table(
    "material_tags",
    Base.metadata,
    Column("material_id", Integer, ForeignKey("materials.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
)


# ── 素材主表 ─────────────────────────────────────────────────────

class Material(Base):
    __tablename__ = "materials"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # 基础信息
    filename = Column(String(500), nullable=False, comment="原始文件名")
    file_path = Column(String(1000), nullable=False, comment="MinIO 对象路径")
    thumbnail_path = Column(String(1000), comment="缩略图路径")
    preview_path = Column(String(1000), comment="预览文件路径")
    file_size = Column(BigInteger, nullable=False, comment="文件大小(字节)")
    file_hash = Column(String(64), index=True, comment="文件MD5哈希（用于去重）")
    mime_type = Column(String(100), comment="MIME类型")
    material_type = Column(Enum(MaterialType), nullable=False, comment="素材类型")

    # 图片属性
    width = Column(Integer, comment="宽度(px)")
    height = Column(Integer, comment="高度(px)")

    # 视频属性
    duration = Column(Float, comment="视频时长(秒)")
    fps = Column(Float, comment="帧率")
    frame_count = Column(Integer, comment="关键帧数量")

    # 管理信息
    title = Column(String(500), comment="素材标题")
    description = Column(Text, comment="素材描述")
    event_name = Column(String(300), index=True, comment="活动名称")
    event_date = Column(DateTime, comment="活动日期")
    status = Column(Enum(MaterialStatus), default=MaterialStatus.PENDING, comment="素材状态")
    security_level = Column(Enum(SecurityLevel), default=SecurityLevel.INTERNAL, comment="密级")
    quality_score = Column(Float, comment="AI质量评分(0-100)")
    is_duplicate = Column(Boolean, default=False, comment="是否为重复素材")
    duplicate_group_id = Column(String(64), comment="重复组ID")

    # OCR / ASR 提取文本
    ocr_text = Column(Text, comment="OCR提取的文字内容")
    asr_text = Column(Text, comment="语音转写的文字内容")

    # 上传信息
    uploaded_by = Column(Integer, ForeignKey("users.id"), comment="上传人ID")
    upload_source = Column(String(100), comment="上传来源(web/migration/api)")

    # 时间
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
    expires_at = Column(DateTime(timezone=True), comment="到期时间（到期自动下架）")

    # 关系
    tags = relationship("Tag", secondary=material_tag_table, back_populates="materials")
    faces = relationship("MaterialFace", back_populates="material", cascade="all, delete-orphan")
    uploader = relationship("User", foreign_keys=[uploaded_by])


# ── 标签表 ───────────────────────────────────────────────────────

class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False, index=True, comment="标签名称")
    category = Column(Enum(TagCategory), default=TagCategory.KEYWORD, comment="标签分类")
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    materials = relationship("Material", secondary=material_tag_table, back_populates="tags")

    class Config:
        # 同名同类标签唯一
        __table_args__ = ({"unique": ("name", "category")},)


# ── 素材人脸关联表 ───────────────────────────────────────────────

class MaterialFace(Base):
    __tablename__ = "material_faces"

    id = Column(Integer, primary_key=True, autoincrement=True)
    material_id = Column(Integer, ForeignKey("materials.id", ondelete="CASCADE"), nullable=False)
    face_library_id = Column(Integer, ForeignKey("face_library.id"), comment="匹配到的已知人脸ID")
    bbox_x = Column(Integer, comment="人脸框x坐标")
    bbox_y = Column(Integer, comment="人脸框y坐标")
    bbox_w = Column(Integer, comment="人脸框宽")
    bbox_h = Column(Integer, comment="人脸框高")
    confidence = Column(Float, comment="识别置信度")
    expression = Column(String(50), comment="表情")
    age = Column(Integer, comment="预估年龄")
    gender = Column(String(10), comment="预估性别")

    material = relationship("Material", back_populates="faces")
    face_person = relationship("FaceLibrary", back_populates="appearances")


# ── 人脸库 ───────────────────────────────────────────────────────

class FaceLibrary(Base):
    __tablename__ = "face_library"

    id = Column(Integer, primary_key=True, autoincrement=True)
    person_name = Column(String(100), nullable=False, index=True, comment="人物姓名")
    person_title = Column(String(200), comment="人物职务")
    department = Column(String(100), comment="所属部门")
    reference_image_path = Column(String(1000), comment="参考照片路径")
    vector_id = Column(String(100), comment="Milvus中的向量ID")
    is_active = Column(Boolean, default=True, comment="是否启用")
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    appearances = relationship("MaterialFace", back_populates="face_person")


# 兼容旧引用名
MaterialTag = material_tag_table
