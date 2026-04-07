"""
测试 Celery 任务 - 使用 mock，不实际连接 broker
"""
from unittest.mock import patch, MagicMock

import pytest


class TestCeleryConfig:
    """Celery 配置测试"""

    def test_celery_app_name(self):
        """Celery app 名称"""
        from app.celery_app import celery_app
        assert celery_app.main == "media_asset_tasks"

    def test_celery_serializer(self):
        """序列化配置"""
        from app.celery_app import celery_app
        assert celery_app.conf.task_serializer == "json"
        assert "json" in celery_app.conf.accept_content

    def test_celery_timezone(self):
        """时区配置"""
        from app.celery_app import celery_app
        assert celery_app.conf.timezone == "Asia/Shanghai"

    def test_celery_concurrency(self):
        """并发配置"""
        from app.celery_app import celery_app
        assert celery_app.conf.worker_concurrency == 4

    def test_celery_timeout(self):
        """超时配置"""
        from app.celery_app import celery_app
        assert celery_app.conf.task_soft_time_limit == 300
        assert celery_app.conf.task_time_limit == 600

    def test_celery_result_expires(self):
        """结果过期时间"""
        from app.celery_app import celery_app
        assert celery_app.conf.result_expires == 86400


class TestAIProcessTasks:
    """AI 处理任务测试"""

    def test_generate_thumbnail_task_exists(self):
        """缩略图任务已注册"""
        from app.tasks.ai_process import generate_thumbnail
        assert callable(generate_thumbnail)

    def test_generate_thumbnail_returns_material_id(self):
        """缩略图任务返回 material_id"""
        from app.tasks.ai_process import generate_thumbnail
        result = generate_thumbnail(42)
        assert result == 42

    def test_extract_metadata_returns_material_id(self):
        """元信息提取返回 material_id"""
        from app.tasks.ai_process import extract_metadata
        result = extract_metadata(99)
        assert result == 99

    def test_run_ocr_task_exists(self):
        """OCR 任务可调用"""
        from app.tasks.ai_process import run_ocr
        assert callable(run_ocr)

    def test_run_clip_task_exists(self):
        """CLIP 任务可调用"""
        from app.tasks.ai_process import run_clip
        assert callable(run_clip)

    def test_run_face_detection_task_exists(self):
        """人脸检测任务可调用"""
        from app.tasks.ai_process import run_face_detection
        assert callable(run_face_detection)

    def test_run_asr_task_exists(self):
        """ASR 任务可调用"""
        from app.tasks.ai_process import run_asr
        assert callable(run_asr)

    def test_run_quality_score_task_exists(self):
        """质量评分任务可调用"""
        from app.tasks.ai_process import run_quality_score
        assert callable(run_quality_score)

    def test_finalize_processing_task_exists(self):
        """最终处理任务可调用"""
        from app.tasks.ai_process import finalize_processing
        assert callable(finalize_processing)


class TestCleanupTasks:
    """清理任务测试"""

    def test_cleanup_expired_task_exists(self):
        """过期清理任务可调用"""
        from app.tasks.cleanup_task import cleanup_expired_materials
        assert callable(cleanup_expired_materials)

    def test_cleanup_duplicate_task_exists(self):
        """重复清理任务可调用"""
        from app.tasks.cleanup_task import cleanup_duplicate_materials
        assert callable(cleanup_duplicate_materials)

    def test_generate_storage_report_task_exists(self):
        """存储报告任务可调用"""
        from app.tasks.cleanup_task import generate_storage_report
        assert callable(generate_storage_report)
