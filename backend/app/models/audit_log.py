"""
审计日志 & 下载记录 模型
"""
import enum
from datetime import datetime, timezone

from sqlalchemy import (
    Column, Integer, String, DateTime, Enum, ForeignKey, Text,
)
from sqlalchemy.orm import relationship

from app.core.database import Base


class ActionType(str, enum.Enum):
    VIEW = "view"               # 预览
    DOWNLOAD = "download"       # 下载
    UPLOAD = "upload"           # 上传
    DELETE = "delete"           # 删除
    EDIT = "edit"               # 编辑
    APPROVE = "approve"         # 审核通过
    REJECT = "reject"           # 审核驳回
    ARCHIVE = "archive"         # 归档
    EXPORT = "export"           # 导出
    SHARE = "share"             # 分享


class AuditLog(Base):
    """全量操作审计日志"""
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="操作人ID")
    action = Column(Enum(ActionType), nullable=False, comment="操作类型")
    resource_type = Column(String(50), nullable=False, comment="资源类型(material/user/tag等)")
    resource_id = Column(Integer, comment="资源ID")
    detail = Column(Text, comment="操作详情(JSON)")
    ip_address = Column(String(50), comment="操作IP")
    user_agent = Column(String(500), comment="浏览器UA")
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    user = relationship("User")


class DownloadRecord(Base):
    """下载记录（独立表，方便快速查询统计）"""
    __tablename__ = "download_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    material_id = Column(Integer, ForeignKey("materials.id"), nullable=False)
    download_purpose = Column(String(200), comment="下载用途")
    ip_address = Column(String(50), comment="下载IP")
    with_watermark = Column(String(10), default="no", comment="是否带水印")
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    user = relationship("User")
    material = relationship("Material")
