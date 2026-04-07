"""
测试 ORM 模型定义 - 枚举值、字段、关系
"""
import pytest


class TestMaterialEnums:
    """素材枚举测试"""

    def test_material_type_values(self):
        """素材类型枚举值"""
        from app.models.material import MaterialType
        assert MaterialType.IMAGE.value == "image"
        assert MaterialType.VIDEO.value == "video"

    def test_material_status_values(self):
        """素材状态枚举值"""
        from app.models.material import MaterialStatus
        assert MaterialStatus.PENDING.value == "pending"
        assert MaterialStatus.PROCESSING.value == "processing"
        assert MaterialStatus.APPROVED.value == "approved"
        assert MaterialStatus.REJECTED.value == "rejected"
        assert MaterialStatus.ARCHIVED.value == "archived"

    def test_security_level_values(self):
        """密级枚举值"""
        from app.models.material import SecurityLevel
        assert SecurityLevel.PUBLIC.value == "public"
        assert SecurityLevel.INTERNAL.value == "internal"
        assert SecurityLevel.RESTRICTED.value == "restricted"
        assert SecurityLevel.CONFIDENTIAL.value == "confidential"

    def test_tag_category_values(self):
        """标签分类枚举值"""
        from app.models.material import TagCategory
        assert TagCategory.PERSON.value == "person"
        assert TagCategory.SCENE.value == "scene"
        assert TagCategory.EVENT.value == "event"
        assert TagCategory.KEYWORD.value == "keyword"
        assert TagCategory.AI_GENERATED.value == "ai_generated"


class TestUserEnums:
    """用户枚举测试"""

    def test_role_enum_values(self):
        """角色枚举值"""
        from app.models.user import RoleEnum
        assert RoleEnum.SUPER_ADMIN.value == "super_admin"
        assert RoleEnum.MANAGER.value == "manager"
        assert RoleEnum.USER.value == "user"
        assert RoleEnum.GUEST.value == "guest"


class TestAuditEnums:
    """审计枚举测试"""

    def test_action_type_values(self):
        """操作类型枚举值"""
        from app.models.audit_log import ActionType
        assert ActionType.VIEW.value == "view"
        assert ActionType.DOWNLOAD.value == "download"
        assert ActionType.UPLOAD.value == "upload"
        assert ActionType.DELETE.value == "delete"
        assert ActionType.APPROVE.value == "approve"
        assert ActionType.REJECT.value == "reject"
        assert ActionType.ARCHIVE.value == "archive"
        assert ActionType.EXPORT.value == "export"
        assert ActionType.SHARE.value == "share"


class TestModelTableNames:
    """模型表名测试"""

    def test_material_table_name(self):
        from app.models.material import Material
        assert Material.__tablename__ == "materials"

    def test_tag_table_name(self):
        from app.models.material import Tag
        assert Tag.__tablename__ == "tags"

    def test_material_face_table_name(self):
        from app.models.material import MaterialFace
        assert MaterialFace.__tablename__ == "material_faces"

    def test_face_library_table_name(self):
        from app.models.material import FaceLibrary
        assert FaceLibrary.__tablename__ == "face_library"

    def test_user_table_name(self):
        from app.models.user import User
        assert User.__tablename__ == "users"

    def test_role_table_name(self):
        from app.models.user import Role
        assert Role.__tablename__ == "roles"

    def test_audit_log_table_name(self):
        from app.models.audit_log import AuditLog
        assert AuditLog.__tablename__ == "audit_logs"

    def test_download_record_table_name(self):
        from app.models.audit_log import DownloadRecord
        assert DownloadRecord.__tablename__ == "download_records"
