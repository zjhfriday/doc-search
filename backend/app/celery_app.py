"""
Celery 应用配置
"""
from celery import Celery

from app.core.config import get_settings

settings = get_settings()

celery_app = Celery(
    "media_asset_tasks",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

celery_app.conf.update(
    # 序列化
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Shanghai",
    enable_utc=True,

    # 任务发现
    task_routes={
        "app.tasks.ai_process.*": {"queue": "ai_queue"},
        "app.tasks.ocr_task.*": {"queue": "ai_queue"},
        "app.tasks.face_task.*": {"queue": "ai_queue"},
        "app.tasks.clip_task.*": {"queue": "ai_queue"},
        "app.tasks.asr_task.*": {"queue": "ai_queue"},
        "app.tasks.video_task.*": {"queue": "ai_queue"},
        "app.tasks.dedup_task.*": {"queue": "default"},
        "app.tasks.quality_task.*": {"queue": "ai_queue"},
        "app.tasks.cleanup_task.*": {"queue": "default"},
    },

    # 并发控制
    worker_concurrency=4,
    worker_prefetch_multiplier=1,

    # 任务超时
    task_soft_time_limit=300,   # 5分钟软超时
    task_time_limit=600,        # 10分钟硬超时

    # 结果过期
    result_expires=86400,       # 结果保留24小时
)

# 自动发现任务模块
celery_app.autodiscover_tasks([
    "app.tasks",
])
