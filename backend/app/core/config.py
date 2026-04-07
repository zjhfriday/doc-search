"""
全局配置 - 基于 pydantic-settings，从环境变量 / .env 文件读取
"""
from pathlib import Path
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # ── Application ──────────────────────────────────────────────
    APP_NAME: str = "media-asset-platform"
    APP_ENV: str = "development"
    DEBUG: bool = True
    SECRET_KEY: str = "change-me-in-production"
    API_V1_PREFIX: str = "/api/v1"

    # ── PostgreSQL ───────────────────────────────────────────────
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "media_asset"

    @property
    def DATABASE_URL(self) -> str:
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    @property
    def DATABASE_URL_SYNC(self) -> str:
        return (
            f"postgresql+psycopg2://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    # ── Redis ────────────────────────────────────────────────────
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: str = ""

    @property
    def REDIS_URL(self) -> str:
        password_part = f":{self.REDIS_PASSWORD}@" if self.REDIS_PASSWORD else ""
        return f"redis://{password_part}{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    # ── Celery ───────────────────────────────────────────────────
    CELERY_BROKER_URL: str = "amqp://guest:guest@localhost:5672//"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/1"

    # ── Elasticsearch ────────────────────────────────────────────
    ES_HOST: str = "localhost"
    ES_PORT: int = 9200
    ES_INDEX_PREFIX: str = "media_asset"

    @property
    def ES_URL(self) -> str:
        return f"http://{self.ES_HOST}:{self.ES_PORT}"

    # ── Milvus ───────────────────────────────────────────────────
    MILVUS_HOST: str = "localhost"
    MILVUS_PORT: int = 19530

    # ── MinIO ────────────────────────────────────────────────────
    MINIO_ENDPOINT: str = "localhost:9000"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin"
    MINIO_BUCKET_ORIGINALS: str = "originals"
    MINIO_BUCKET_THUMBNAILS: str = "thumbnails"
    MINIO_BUCKET_PREVIEWS: str = "previews"
    MINIO_SECURE: bool = False

    # ── AI Models ────────────────────────────────────────────────
    CLIP_MODEL_NAME: str = "ViT-B-16"
    CLIP_MODEL_PRETRAINED: str = "openai"
    INSIGHTFACE_MODEL: str = "buffalo_l"
    PADDLEOCR_LANG: str = "ch"
    ASR_MODEL: str = "paraformer-zh"

    # ── JWT ──────────────────────────────────────────────────────
    JWT_SECRET_KEY: str = "change-me-jwt-secret"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 480

    # ── Upload ───────────────────────────────────────────────────
    MAX_UPLOAD_SIZE_MB: int = 500
    ALLOWED_IMAGE_TYPES: str = "jpg,jpeg,png,bmp,tiff,webp"
    ALLOWED_VIDEO_TYPES: str = "mp4,avi,mov,mkv,flv,wmv"

    @property
    def allowed_image_extensions(self) -> set[str]:
        return {f".{ext.strip()}" for ext in self.ALLOWED_IMAGE_TYPES.split(",")}

    @property
    def allowed_video_extensions(self) -> set[str]:
        return {f".{ext.strip()}" for ext in self.ALLOWED_VIDEO_TYPES.split(",")}

    # ── Paths ────────────────────────────────────────────────────
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    UPLOAD_DIR: Path = BASE_DIR / "uploads"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
