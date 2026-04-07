"""
测试 app.core.config - 配置模块
"""
import os
from unittest.mock import patch

import pytest


class TestSettings:
    """配置类测试"""

    def test_database_url_property(self):
        """测试 DATABASE_URL 拼接"""
        with patch.dict(os.environ, {
            "POSTGRES_HOST": "db.test.com",
            "POSTGRES_PORT": "5433",
            "POSTGRES_USER": "myuser",
            "POSTGRES_PASSWORD": "mypass",
            "POSTGRES_DB": "mydb",
        }, clear=False):
            from app.core.config import Settings
            s = Settings()
            assert "db.test.com" in s.DATABASE_URL
            assert "5433" in s.DATABASE_URL
            assert "myuser" in s.DATABASE_URL
            assert "mypass" in s.DATABASE_URL
            assert "mydb" in s.DATABASE_URL
            assert s.DATABASE_URL.startswith("postgresql+asyncpg://")

    def test_database_url_sync_property(self):
        """测试同步 DATABASE_URL 拼接"""
        with patch.dict(os.environ, {
            "POSTGRES_HOST": "localhost",
            "POSTGRES_PORT": "5432",
            "POSTGRES_USER": "pg",
            "POSTGRES_PASSWORD": "pg",
            "POSTGRES_DB": "testdb",
        }, clear=False):
            from app.core.config import Settings
            s = Settings()
            assert s.DATABASE_URL_SYNC.startswith("postgresql+psycopg2://")

    def test_redis_url_without_password(self):
        """测试 Redis URL 无密码"""
        with patch.dict(os.environ, {
            "REDIS_HOST": "redis.local",
            "REDIS_PORT": "6380",
            "REDIS_DB": "2",
            "REDIS_PASSWORD": "",
        }, clear=False):
            from app.core.config import Settings
            s = Settings()
            assert s.REDIS_URL == "redis://redis.local:6380/2"

    def test_redis_url_with_password(self):
        """测试 Redis URL 有密码"""
        with patch.dict(os.environ, {
            "REDIS_HOST": "redis.local",
            "REDIS_PORT": "6379",
            "REDIS_DB": "0",
            "REDIS_PASSWORD": "secret",
        }, clear=False):
            from app.core.config import Settings
            s = Settings()
            assert ":secret@" in s.REDIS_URL

    def test_es_url(self):
        """测试 ES URL"""
        with patch.dict(os.environ, {
            "ES_HOST": "es.local",
            "ES_PORT": "9201",
        }, clear=False):
            from app.core.config import Settings
            s = Settings()
            assert s.ES_URL == "http://es.local:9201"

    def test_allowed_image_extensions(self):
        """测试图片扩展名解析"""
        with patch.dict(os.environ, {
            "ALLOWED_IMAGE_TYPES": "jpg,png,webp",
        }, clear=False):
            from app.core.config import Settings
            s = Settings()
            exts = s.allowed_image_extensions
            assert ".jpg" in exts
            assert ".png" in exts
            assert ".webp" in exts
            assert ".mp4" not in exts

    def test_allowed_video_extensions(self):
        """测试视频扩展名解析"""
        with patch.dict(os.environ, {
            "ALLOWED_VIDEO_TYPES": "mp4,avi",
        }, clear=False):
            from app.core.config import Settings
            s = Settings()
            exts = s.allowed_video_extensions
            assert ".mp4" in exts
            assert ".avi" in exts

    def test_default_values(self):
        """测试默认值"""
        from app.core.config import Settings
        s = Settings()
        assert s.APP_NAME == "media-asset-platform"
        assert s.JWT_ALGORITHM == "HS256"
        assert s.MAX_UPLOAD_SIZE_MB == 500
        assert s.MINIO_SECURE is False
