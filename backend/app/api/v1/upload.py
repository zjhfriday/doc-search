"""
素材上传接口 - 单文件 / 批量 / 打包上传
"""
import hashlib
from typing import List, Optional

from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.material import Material, MaterialType, MaterialStatus, SecurityLevel

router = APIRouter()
settings = get_settings()


def _detect_material_type(filename: str) -> MaterialType:
    """根据文件扩展名判断素材类型"""
    ext = "." + filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if ext in settings.allowed_image_extensions:
        return MaterialType.IMAGE
    elif ext in settings.allowed_video_extensions:
        return MaterialType.VIDEO
    else:
        raise HTTPException(
            status_code=400,
            detail=f"不支持的文件类型: {ext}",
        )


@router.post("/single", summary="单文件上传")
async def upload_single(
    file: UploadFile = File(..., description="素材文件"),
    event_name: Optional[str] = Form(None, description="活动名称"),
    event_date: Optional[str] = Form(None, description="活动日期"),
    security_level: str = Form("internal", description="密级"),
    description: Optional[str] = Form(None, description="素材描述"),
    tags: Optional[str] = Form(None, description="标签(逗号分隔)"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    单文件上传流程:
    1. 校验文件类型和大小
    2. 计算文件哈希（去重依据）
    3. 上传到 MinIO
    4. 写入数据库
    5. 触发 Celery AI处理流水线
    """
    # 校验文件大小
    content = await file.read()
    file_size = len(content)
    if file_size > settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024:
        raise HTTPException(status_code=400, detail="文件超过最大允许大小")

    # 检测素材类型
    material_type = _detect_material_type(file.filename)

    # 计算文件哈希
    file_hash = hashlib.md5(content).hexdigest()

    # TODO: 上传到 MinIO
    # minio_client = get_minio_client()
    # object_name = f"{material_type.value}/{file_hash[:2]}/{file_hash}/{file.filename}"
    # minio_client.put_object(...)

    # 写入数据库
    material = Material(
        filename=file.filename,
        file_path=f"{material_type.value}/{file_hash}/{file.filename}",
        file_size=file_size,
        file_hash=file_hash,
        mime_type=file.content_type,
        material_type=material_type,
        event_name=event_name,
        security_level=SecurityLevel(security_level) if security_level else SecurityLevel.INTERNAL,
        description=description,
        status=MaterialStatus.PROCESSING,
        uploaded_by=current_user.id,
        upload_source="web",
    )
    db.add(material)
    await db.flush()

    # TODO: 触发 AI 处理流水线
    # from app.tasks.ai_process import ai_process_pipeline
    # ai_process_pipeline.delay(material.id)

    return {
        "message": "上传成功，AI处理中",
        "material_id": material.id,
        "filename": file.filename,
        "file_size": file_size,
        "material_type": material_type.value,
    }


@router.post("/batch", summary="批量上传")
async def upload_batch(
    files: List[UploadFile] = File(..., description="多个素材文件"),
    event_name: Optional[str] = Form(None),
    security_level: str = Form("internal"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    批量上传多个文件
    """
    results = []
    for file in files:
        try:
            content = await file.read()
            file_size = len(content)
            material_type = _detect_material_type(file.filename)
            file_hash = hashlib.md5(content).hexdigest()

            material = Material(
                filename=file.filename,
                file_path=f"{material_type.value}/{file_hash}/{file.filename}",
                file_size=file_size,
                file_hash=file_hash,
                mime_type=file.content_type,
                material_type=material_type,
                event_name=event_name,
                security_level=SecurityLevel(security_level),
                status=MaterialStatus.PROCESSING,
                uploaded_by=current_user.id,
                upload_source="web_batch",
            )
            db.add(material)
            await db.flush()

            results.append({
                "filename": file.filename,
                "material_id": material.id,
                "status": "success",
            })
        except Exception as e:
            results.append({
                "filename": file.filename,
                "status": "error",
                "error": str(e),
            })

    return {
        "message": f"批量上传完成: {len(results)} 个文件",
        "results": results,
    }
