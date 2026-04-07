"""
ORM 模型汇总 - 确保 Alembic 能发现所有模型
"""
from app.models.user import User, Role
from app.models.material import Material, MaterialTag, Tag, MaterialFace, FaceLibrary
from app.models.audit_log import AuditLog, DownloadRecord

__all__ = [
    "User",
    "Role",
    "Material",
    "MaterialTag",
    "Tag",
    "MaterialFace",
    "FaceLibrary",
    "AuditLog",
    "DownloadRecord",
]
