"""
数据看板接口 - 运营数据统计
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.database import get_db
from app.core.security import get_current_user, require_roles
from app.models.user import User
from app.models.material import Material, MaterialType, MaterialStatus
from app.models.audit_log import DownloadRecord

router = APIRouter()


@router.get("/overview", summary="总览数据")
async def get_overview(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("super_admin", "manager")),
):
    """获取平台总览统计数据"""

    # 素材总数
    total_materials = (await db.execute(
        select(func.count()).select_from(Material)
    )).scalar()

    # 按类型统计
    image_count = (await db.execute(
        select(func.count()).select_from(Material)
        .where(Material.material_type == MaterialType.IMAGE)
    )).scalar()

    video_count = (await db.execute(
        select(func.count()).select_from(Material)
        .where(Material.material_type == MaterialType.VIDEO)
    )).scalar()

    # 按状态统计
    pending_count = (await db.execute(
        select(func.count()).select_from(Material)
        .where(Material.status == MaterialStatus.PENDING)
    )).scalar()

    processing_count = (await db.execute(
        select(func.count()).select_from(Material)
        .where(Material.status == MaterialStatus.PROCESSING)
    )).scalar()

    # 总存储大小
    total_size = (await db.execute(
        select(func.sum(Material.file_size))
    )).scalar() or 0

    # 下载总次数
    download_count = (await db.execute(
        select(func.count()).select_from(DownloadRecord)
    )).scalar()

    # 用户总数
    user_count = (await db.execute(
        select(func.count()).select_from(User)
    )).scalar()

    return {
        "total_materials": total_materials,
        "image_count": image_count,
        "video_count": video_count,
        "pending_count": pending_count,
        "processing_count": processing_count,
        "total_size_bytes": total_size,
        "total_size_gb": round(total_size / (1024 ** 3), 2),
        "download_count": download_count,
        "user_count": user_count,
    }


@router.get("/storage", summary="存储监控")
async def get_storage_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("super_admin", "manager")),
):
    """获取存储使用情况统计"""
    # 按素材类型统计存储
    results = await db.execute(
        select(
            Material.material_type,
            func.count().label("count"),
            func.sum(Material.file_size).label("total_size"),
        ).group_by(Material.material_type)
    )

    storage_by_type = [
        {
            "type": row.material_type.value if row.material_type else "unknown",
            "count": row.count,
            "total_size_bytes": row.total_size or 0,
            "total_size_gb": round((row.total_size or 0) / (1024 ** 3), 2),
        }
        for row in results.all()
    ]

    return {"storage_by_type": storage_by_type}
