"""
API v1 路由汇总
"""
from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.material import router as material_router
from app.api.v1.search import router as search_router
from app.api.v1.upload import router as upload_router
from app.api.v1.audit import router as audit_router
from app.api.v1.user import router as user_router
from app.api.v1.dashboard import router as dashboard_router
from app.api.v1.face_library import router as face_library_router

router = APIRouter()

router.include_router(auth_router, prefix="/auth", tags=["认证"])
router.include_router(material_router, prefix="/materials", tags=["素材管理"])
router.include_router(search_router, prefix="/search", tags=["素材检索"])
router.include_router(upload_router, prefix="/upload", tags=["素材上传"])
router.include_router(audit_router, prefix="/audit", tags=["审计日志"])
router.include_router(user_router, prefix="/users", tags=["用户管理"])
router.include_router(dashboard_router, prefix="/dashboard", tags=["数据看板"])
router.include_router(face_library_router, prefix="/face-library", tags=["人脸库"])
