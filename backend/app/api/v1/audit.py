"""
审计日志接口
"""
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.security import require_roles
from app.models.audit_log import AuditLog, DownloadRecord, ActionType
from app.models.user import User

router = APIRouter()


@router.get("/logs", summary="查询操作日志")
async def list_audit_logs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    action: Optional[ActionType] = Query(None),
    user_id: Optional[int] = Query(None),
    resource_type: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("super_admin", "manager")),
):
    """查询操作审计日志（管理员）"""
    query = select(AuditLog).options(selectinload(AuditLog.user))

    if action:
        query = query.where(AuditLog.action == action)
    if user_id:
        query = query.where(AuditLog.user_id == user_id)
    if resource_type:
        query = query.where(AuditLog.resource_type == resource_type)

    # 总数
    count_q = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_q)).scalar()

    # 分页
    query = query.order_by(AuditLog.created_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    logs = result.scalars().all()

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": [
            {
                "id": log.id,
                "user_id": log.user_id,
                "username": log.user.username if log.user else None,
                "action": log.action.value,
                "resource_type": log.resource_type,
                "resource_id": log.resource_id,
                "detail": log.detail,
                "ip_address": log.ip_address,
                "created_at": log.created_at.isoformat() if log.created_at else None,
            }
            for log in logs
        ],
    }


@router.get("/downloads", summary="查询下载记录")
async def list_download_records(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    user_id: Optional[int] = Query(None),
    material_id: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("super_admin", "manager")),
):
    """查询下载记录（管理员）"""
    query = select(DownloadRecord).options(
        selectinload(DownloadRecord.user),
        selectinload(DownloadRecord.material),
    )

    if user_id:
        query = query.where(DownloadRecord.user_id == user_id)
    if material_id:
        query = query.where(DownloadRecord.material_id == material_id)

    count_q = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_q)).scalar()

    query = query.order_by(DownloadRecord.created_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    records = result.scalars().all()

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": [
            {
                "id": r.id,
                "user_id": r.user_id,
                "username": r.user.username if r.user else None,
                "material_id": r.material_id,
                "filename": r.material.filename if r.material else None,
                "download_purpose": r.download_purpose,
                "ip_address": r.ip_address,
                "with_watermark": r.with_watermark,
                "created_at": r.created_at.isoformat() if r.created_at else None,
            }
            for r in records
        ],
    }
