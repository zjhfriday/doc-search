"""
定期清理任务 - 过期素材下架、低质量清理、存储释放
"""
from loguru import logger

from app.celery_app import celery_app


@celery_app.task(name="tasks.cleanup_expired_materials")
def cleanup_expired_materials():
    """
    清理过期素材
    - 检查 materials.expires_at
    - 将过期素材状态改为 ARCHIVED
    """
    logger.info("🧹 开始清理过期素材...")
    # TODO: 查询所有 expires_at < now() 且状态非 ARCHIVED 的素材
    # 将其状态改为 ARCHIVED


@celery_app.task(name="tasks.cleanup_duplicate_materials")
def cleanup_duplicate_materials():
    """
    清理重复素材
    - 保留质量最高的一份
    - 其余标记为重复
    """
    logger.info("🧹 开始清理重复素材...")
    # TODO: 按 duplicate_group_id 分组，每组保留 quality_score 最高的


@celery_app.task(name="tasks.generate_storage_report")
def generate_storage_report():
    """
    生成存储报告
    - 统计各类型素材占用空间
    - 统计重复素材占用空间
    - 生成清理建议
    """
    logger.info("📊 生成存储报告...")
    # TODO: 统计并输出报告
