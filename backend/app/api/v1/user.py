"""
用户管理接口
"""
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.database import get_db
from app.core.security import get_current_user, require_roles, hash_password
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate, UserResponse

router = APIRouter()


@router.get("", summary="用户列表")
async def list_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    keyword: Optional[str] = Query(None, description="搜索关键词"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("super_admin")),
):
    """获取用户列表（超级管理员）"""
    query = select(User)

    if keyword:
        query = query.where(
            User.username.ilike(f"%{keyword}%")
            | User.display_name.ilike(f"%{keyword}%")
        )

    count_q = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_q)).scalar()

    query = query.order_by(User.created_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    users = result.scalars().all()

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": [UserResponse.model_validate(u) for u in users],
    }


@router.post("", response_model=UserResponse, summary="创建用户")
async def create_user(
    data: UserCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("super_admin")),
):
    """创建新用户（超级管理员）"""
    # 检查用户名唯一
    existing = await db.execute(select(User).where(User.username == data.username))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="用户名已存在")

    user = User(
        username=data.username,
        hashed_password=hash_password(data.password),
        display_name=data.display_name,
        email=data.email,
        department=data.department,
        role=data.role,
    )
    db.add(user)
    await db.flush()

    return UserResponse.model_validate(user)


@router.put("/{user_id}", response_model=UserResponse, summary="更新用户")
async def update_user(
    user_id: int,
    data: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("super_admin")),
):
    """更新用户信息（超级管理员）"""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)

    await db.flush()
    return UserResponse.model_validate(user)
