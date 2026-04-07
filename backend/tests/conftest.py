"""
测试基础设施 - fixtures, mock 工具, 测试数据库
"""
import os
import sys
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# 确保 backend/app 在 Python 路径中
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# 在导入 app 模块前 mock 掉外部依赖
# 避免在测试时真正连接 PostgreSQL / Redis / MinIO / Milvus 等


@pytest.fixture
def mock_settings():
    """提供测试用配置"""
    with patch("app.core.config.get_settings") as mock:
        settings = MagicMock()
        settings.APP_NAME = "test-app"
        settings.APP_ENV = "testing"
        settings.DEBUG = True
        settings.SECRET_KEY = "test-secret"
        settings.API_V1_PREFIX = "/api/v1"

        settings.POSTGRES_HOST = "localhost"
        settings.POSTGRES_PORT = 5432
        settings.POSTGRES_USER = "test"
        settings.POSTGRES_PASSWORD = "test"
        settings.POSTGRES_DB = "test_db"
        settings.DATABASE_URL = "postgresql+asyncpg://test:test@localhost:5432/test_db"

        settings.REDIS_HOST = "localhost"
        settings.REDIS_PORT = 6379
        settings.REDIS_DB = 0
        settings.REDIS_PASSWORD = ""
        settings.REDIS_URL = "redis://localhost:6379/0"

        settings.CELERY_BROKER_URL = "amqp://guest:guest@localhost:5672//"
        settings.CELERY_RESULT_BACKEND = "redis://localhost:6379/1"

        settings.ES_HOST = "localhost"
        settings.ES_PORT = 9200
        settings.ES_INDEX_PREFIX = "test_media"
        settings.ES_URL = "http://localhost:9200"

        settings.MILVUS_HOST = "localhost"
        settings.MILVUS_PORT = 19530

        settings.MINIO_ENDPOINT = "localhost:9000"
        settings.MINIO_ACCESS_KEY = "minioadmin"
        settings.MINIO_SECRET_KEY = "minioadmin"
        settings.MINIO_BUCKET_ORIGINALS = "test-originals"
        settings.MINIO_BUCKET_THUMBNAILS = "test-thumbnails"
        settings.MINIO_BUCKET_PREVIEWS = "test-previews"
        settings.MINIO_SECURE = False

        settings.CLIP_MODEL_NAME = "ViT-B-16"
        settings.CLIP_MODEL_PRETRAINED = "openai"
        settings.INSIGHTFACE_MODEL = "buffalo_l"
        settings.PADDLEOCR_LANG = "ch"
        settings.ASR_MODEL = "paraformer-zh"

        settings.JWT_SECRET_KEY = "test-jwt-secret"
        settings.JWT_ALGORITHM = "HS256"
        settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES = 480

        settings.MAX_UPLOAD_SIZE_MB = 500
        settings.ALLOWED_IMAGE_TYPES = "jpg,jpeg,png,bmp,tiff,webp"
        settings.ALLOWED_VIDEO_TYPES = "mp4,avi,mov,mkv,flv,wmv"
        settings.allowed_image_extensions = {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".webp"}
        settings.allowed_video_extensions = {".mp4", ".avi", ".mov", ".mkv", ".flv", ".wmv"}

        settings.UPLOAD_DIR = MagicMock()

        mock.return_value = settings
        yield settings


@pytest.fixture
def mock_db():
    """提供 mock 的异步数据库 Session"""
    db = AsyncMock()
    db.execute = AsyncMock()
    db.flush = AsyncMock()
    db.commit = AsyncMock()
    db.rollback = AsyncMock()
    db.close = AsyncMock()
    db.add = MagicMock()
    db.delete = AsyncMock()
    return db


@pytest.fixture
def sample_user():
    """创建测试用户对象"""
    user = MagicMock()
    user.id = 1
    user.username = "testuser"
    user.display_name = "Test User"
    user.email = "test@example.com"
    user.department = "技术部"
    user.role = "user"
    user.is_active = True
    user.hashed_password = "$2b$12$test_hashed_password"
    user.last_login_at = None
    user.created_at = datetime(2024, 1, 1, tzinfo=timezone.utc)
    user.updated_at = datetime(2024, 1, 1, tzinfo=timezone.utc)
    return user


@pytest.fixture
def admin_user():
    """创建管理员用户"""
    user = MagicMock()
    user.id = 2
    user.username = "admin"
    user.display_name = "Admin"
    user.email = "admin@example.com"
    user.department = "管理部"
    user.role = "super_admin"
    user.is_active = True
    user.hashed_password = "$2b$12$admin_hashed_password"
    user.last_login_at = None
    user.created_at = datetime(2024, 1, 1, tzinfo=timezone.utc)
    user.updated_at = datetime(2024, 1, 1, tzinfo=timezone.utc)
    return user


@pytest.fixture
def sample_material():
    """创建测试素材对象"""
    material = MagicMock()
    material.id = 1
    material.filename = "test_photo.jpg"
    material.file_path = "image/ab/abcdef123456/test_photo.jpg"
    material.thumbnail_path = "thumbnails/test_photo_thumb.jpg"
    material.file_size = 1024000
    material.file_hash = "abcdef1234567890abcdef1234567890"
    material.mime_type = "image/jpeg"
    material.material_type = "image"
    material.width = 1920
    material.height = 1080
    material.duration = None
    material.title = "测试照片"
    material.description = "这是一张测试照片"
    material.event_name = "2024年表彰大会"
    material.event_date = datetime(2024, 6, 1, tzinfo=timezone.utc)
    material.status = "approved"
    material.security_level = "internal"
    material.quality_score = 85.5
    material.is_duplicate = False
    material.ocr_text = "测试文字"
    material.asr_text = None
    material.uploaded_by = 1
    material.created_at = datetime(2024, 1, 1, tzinfo=timezone.utc)
    material.updated_at = datetime(2024, 1, 1, tzinfo=timezone.utc)
    material.tags = []
    material.faces = []
    return material
