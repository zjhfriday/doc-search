"""
素材管理接口 - CRUD / 审核 / 归档
"""
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.security import get_current_user, require_roles
from app.models.user import User
from app.models.material import Material, MaterialStatus
from app.schemas.material import (
    MaterialResponse, MaterialListResponse, MaterialUpdate,
)

router = APIRouter()


@router.get("", response_model=MaterialListResponse, summary="素材列表")
async def list_materials(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status_filter: Optional[MaterialStatus] = Query(None, alias="status"),
    material_type: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """分页获取素材列表，支持状态和类型过滤"""
    query = select(Material).options(
        selectinload(Material.tags),
        selectinload(Material.faces),
    )

    if status_filter:
        query = query.where(Material.status == status_filter)
    if material_type:
        query = query.where(Material.material_type == material_type)

    # 总数
    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar()

    # 分页
    query = query.order_by(Material.created_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    materials = result.scalars().all()

    return MaterialListResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=[MaterialResponse.model_validate(m) for m in materials],
    )


@router.get("/{material_id}", response_model=MaterialResponse, summary="素材详情")
async def get_material(
    material_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取单个素材详情"""
    result = await db.execute(
        select(Material)
        .options(selectinload(Material.tags), selectinload(Material.faces))
        .where(Material.id == material_id)
    )
    material = result.scalar_one_or_none()

    if not material:
        raise HTTPException(status_code=404, detail="素材不存在")

    # TODO: 权限检查 - 根据用户角色和素材密级判断可见性
    return MaterialResponse.model_validate(material)


@router.put("/{material_id}", response_model=MaterialResponse, summary="更新素材信息")
async def update_material(
    material_id: int,
    data: MaterialUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("super_admin", "manager")),
):
    """更新素材元信息（管理员/素材管理员）"""
    result = await db.execute(select(Material).where(Material.id == material_id))
    material = result.scalar_one_or_none()

    if not material:
        raise HTTPException(status_code=404, detail="素材不存在")

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if field != "tags":  # tags 需要单独处理
            setattr(material, field, value)

    await db.flush()
    return MaterialResponse.model_validate(material)


@router.delete("/{material_id}", summary="删除素材")
async def delete_material(
    material_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("super_admin", "manager")),
):
    """删除素材（管理员/素材管理员）"""
    result = await db.execute(select(Material).where(Material.id == material_id))
    material = result.scalar_one_or_none()

    if not material:
        raise HTTPException(status_code=404, detail="素材不存在")

    await db.delete(material)
    await db.flush()
    # TODO: 同步删除 MinIO 文件、Milvus 向量、ES 索引

    return {"message": "素材已删除", "id": material_id}


@router.post("/{material_id}/approve", summary="审核通过")
async def approve_material(
    material_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("super_admin", "manager")),
):
    result = await db.execute(select(Material).where(Material.id == material_id))
    material = result.scalar_one_or_none()
    if not material:
        raise HTTPException(status_code=404, detail="素材不存在")

    material.status = MaterialStatus.APPROVED
    await db.flush()
    return {"message": "素材已审核通过", "id": material_id}


@router.post("/{material_id}/reject", summary="审核驳回")
async def reject_material(
    material_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("super_admin", "manager")),
):
    result = await db.execute(select(Material).where(Material.id == material_id))
    material = result.scalar_one_or_none()
    if not material:
        raise HTTPException(status_code=404, detail="素材不存在")

    material.status = MaterialStatus.REJECTED
    await db.flush()
    return {"message": "素材已驳回", "id": material_id}
