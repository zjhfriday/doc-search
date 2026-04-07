"""
FastAPI 应用入口
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from app.core.config import get_settings
from app.core.database import init_db
from app.api.v1 import router as api_v1_router

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    logger.info(f"🚀 {settings.APP_NAME} 启动中...")

    # 启动时初始化
    if settings.APP_ENV == "development":
        await init_db()
        logger.info("✅ 数据库表初始化完成（开发模式）")

    # 确保上传目录存在
    settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    logger.info(f"✅ {settings.APP_NAME} 启动完成")
    yield

    # 关闭时清理
    logger.info(f"🛑 {settings.APP_NAME} 正在关闭...")


def create_app() -> FastAPI:
    """应用工厂"""
    app = FastAPI(
        title="党群素材智能检索平台",
        description="图片/视频素材智能检索与治理平台 API",
        version="1.0.0",
        docs_url="/docs" if settings.DEBUG else None,
        redoc_url="/redoc" if settings.DEBUG else None,
        lifespan=lifespan,
    )

    # CORS 中间件
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"] if settings.DEBUG else [],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 注册路由
    app.include_router(api_v1_router, prefix=settings.API_V1_PREFIX)

    # 健康检查
    @app.get("/health", tags=["系统"])
    async def health_check():
        return {"status": "healthy", "app": settings.APP_NAME}

    return app


app = create_app()
