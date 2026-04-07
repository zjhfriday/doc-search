"""
素材管理服务
"""
from typing import Optional, List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from loguru import logger

from app.models.material import Material, MaterialStatus, Tag, TagCategory, material_tag_table


class MaterialService:
    """素材管理业务逻辑"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_or_create_tag(self, name: str, category: TagCategory = TagCategory.KEYWORD) -> Tag:
        """获取或创建标签"""
        result = await self.db.execute(
            select(Tag).where(Tag.name == name, Tag.category == category)
        )
        tag = result.scalar_one_or_none()

        if not tag:
            tag = Tag(name=name, category=category)
            self.db.add(tag)
            await self.db.flush()

        return tag

    async def add_tags_to_material(
        self,
        material_id: int,
        tag_names: List[str],
        category: TagCategory = TagCategory.KEYWORD,
    ):
        """为素材添加标签"""
        for name in tag_names:
            tag = await self.get_or_create_tag(name, category)
            await self.db.execute(
                material_tag_table.insert().values(
                    material_id=material_id,
                    tag_id=tag.id,
                ).prefix_with("OR IGNORE")
            )

    async def update_material_status(
        self, material_id: int, status: MaterialStatus
    ):
        """更新素材状态"""
        await self.db.execute(
            update(Material)
            .where(Material.id == material_id)
            .values(status=status)
        )
        logger.info(f"素材状态更新: id={material_id}, status={status.value}")

    async def check_duplicate_by_hash(self, file_hash: str) -> Optional[Material]:
        """通过文件哈希检查重复"""
        result = await self.db.execute(
            select(Material).where(Material.file_hash == file_hash)
        )
        return result.scalar_one_or_none()
