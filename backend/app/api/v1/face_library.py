"""
人脸库管理接口
"""
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.database import get_db
from app.core.security import require_roles
from app.models.material import FaceLibrary
from app.models.user import User

router = APIRouter()


@router.get("", summary="人脸库列表")
async def list_faces(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    keyword: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("super_admin", "manager")),
):
    """获取人脸库列表"""
    query = select(FaceLibrary)
    if keyword:
        query = query.where(FaceLibrary.person_name.ilike(f"%{keyword}%"))

    count_q = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_q)).scalar()

    query = query.order_by(FaceLibrary.created_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    faces = result.scalars().all()

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": [
            {
                "id": f.id,
                "person_name": f.person_name,
                "person_title": f.person_title,
                "department": f.department,
                "is_active": f.is_active,
                "created_at": f.created_at.isoformat() if f.created_at else None,
            }
            for f in faces
        ],
    }


@router.post("", summary="添加人脸")
async def add_face(
    person_name: str = Form(..., description="人物姓名"),
    person_title: Optional[str] = Form(None, description="人物职务"),
    department: Optional[str] = Form(None, description="所属部门"),
    photo: UploadFile = File(..., description="参考人脸照片"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("super_admin", "manager")),
):
    """
    添加人脸到人脸库:
    1. 用 InsightFace 提取人脸特征向量
    2. 存入 Milvus face_vectors collection
    3. 写入数据库
    """
    # TODO: InsightFace 提取特征 → Milvus 存储
    face = FaceLibrary(
        person_name=person_name,
        person_title=person_title,
        department=department,
        reference_image_path=f"face_library/{person_name}_{photo.filename}",
    )
    db.add(face)
    await db.flush()

    return {
        "message": "人脸添加成功",
        "id": face.id,
        "person_name": person_name,
    }


@router.delete("/{face_id}", summary="删除人脸")
async def delete_face(
    face_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("super_admin", "manager")),
):
    result = await db.execute(select(FaceLibrary).where(FaceLibrary.id == face_id))
    face = result.scalar_one_or_none()
    if not face:
        raise HTTPException(status_code=404, detail="人脸记录不存在")

    await db.delete(face)
    await db.flush()
    # TODO: 同步删除 Milvus 中的向量

    return {"message": "人脸已删除", "id": face_id}
