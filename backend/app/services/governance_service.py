"""
素材治理服务 - 去重、清理、归档、生命周期管理
"""
from datetime import datetime, timezone
from typing import List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func
from loguru import logger

from app.models.material import Material, MaterialStatus


class GovernanceService:
    """素材治理业务逻辑"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def archive_expired_materials(self) -> int:
        """归档过期素材"""
        now = datetime.now(timezone.utc)
        result = await self.db.execute(
            update(Material)
            .where(
                Material.expires_at <= now,
                Material.status != MaterialStatus.ARCHIVED,
            )
            .values(status=MaterialStatus.ARCHIVED)
        )
        count = result.rowcount
        logger.info(f"已归档 {count} 个过期素材")
        return count

    async def get_duplicate_groups(self) -> List[dict]:
        """获取重复素材分组"""
        result = await self.db.execute(
            select(
                Material.file_hash,
                func.count().label("count"),
            )
            .where(Material.file_hash.isnot(None))
            .group_by(Material.file_hash)
            .having(func.count() > 1)
        )

        groups = []
        for row in result.all():
            materials = await self.db.execute(
                select(Material).where(Material.file_hash == row.file_hash)
            )
            items = materials.scalars().all()
            groups.append({
                "file_hash": row.file_hash,
                "count": row.count,
                "materials": [
                    {
                        "id": m.id,
                        "filename": m.filename,
                        "quality_score": m.quality_score,
                        "created_at": m.created_at.isoformat() if m.created_at else None,
                    }
                    for m in items
                ],
            })

        return groups

    async def get_storage_stats(self) -> dict:
        """获取存储统计信息"""
        total_size = (await self.db.execute(
            select(func.sum(Material.file_size))
        )).scalar() or 0

        total_count = (await self.db.execute(
            select(func.count()).select_from(Material)
        )).scalar()

        duplicate_count = (await self.db.execute(
            select(func.count()).select_from(Material).where(Material.is_duplicate == True)
        )).scalar()

        return {
            "total_count": total_count,
            "total_size_bytes": total_size,
            "total_size_gb": round(total_size / (1024 ** 3), 2),
            "duplicate_count": duplicate_count,
        }
