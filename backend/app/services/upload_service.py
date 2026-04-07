"""
上传服务 - MinIO 文件上传与管理
"""
import io
import hashlib
from typing import Optional
from pathlib import Path

from loguru import logger
from minio import Minio

from app.core.config import get_settings
from app.core.dependencies import get_minio_client

settings = get_settings()


class UploadService:
    """素材文件上传管理服务"""

    def __init__(self):
        self.client: Minio = get_minio_client()
        self._ensure_buckets()

    def _ensure_buckets(self):
        """确保所有必要的存储桶存在"""
        buckets = [
            settings.MINIO_BUCKET_ORIGINALS,
            settings.MINIO_BUCKET_THUMBNAILS,
            settings.MINIO_BUCKET_PREVIEWS,
        ]
        for bucket in buckets:
            if not self.client.bucket_exists(bucket):
                self.client.make_bucket(bucket)
                logger.info(f"✅ 创建 MinIO Bucket: {bucket}")

    def upload_file(
        self,
        file_content: bytes,
        object_name: str,
        bucket: Optional[str] = None,
        content_type: str = "application/octet-stream",
    ) -> str:
        """
        上传文件到 MinIO

        Args:
            file_content: 文件内容
            object_name: 对象名称 (路径)
            bucket: 存储桶名称
            content_type: MIME 类型

        Returns:
            对象路径
        """
        bucket = bucket or settings.MINIO_BUCKET_ORIGINALS

        self.client.put_object(
            bucket_name=bucket,
            object_name=object_name,
            data=io.BytesIO(file_content),
            length=len(file_content),
            content_type=content_type,
        )
        logger.info(f"📤 文件已上传: {bucket}/{object_name}")
        return f"{bucket}/{object_name}"

    def get_presigned_url(
        self,
        object_name: str,
        bucket: Optional[str] = None,
        expires_hours: int = 1,
    ) -> str:
        """
        生成预签名下载 URL

        Args:
            object_name: 对象名称
            bucket: 存储桶
            expires_hours: URL有效期(小时)

        Returns:
            预签名 URL
        """
        from datetime import timedelta

        bucket = bucket or settings.MINIO_BUCKET_ORIGINALS
        url = self.client.presigned_get_object(
            bucket_name=bucket,
            object_name=object_name,
            expires=timedelta(hours=expires_hours),
        )
        return url

    def delete_file(
        self,
        object_name: str,
        bucket: Optional[str] = None,
    ):
        """删除 MinIO 中的文件"""
        bucket = bucket or settings.MINIO_BUCKET_ORIGINALS
        self.client.remove_object(bucket_name=bucket, object_name=object_name)
        logger.info(f"🗑️ 文件已删除: {bucket}/{object_name}")

    @staticmethod
    def generate_object_path(
        material_type: str, file_hash: str, filename: str
    ) -> str:
        """
        生成 MinIO 对象路径

        格式: {type}/{hash前2位}/{hash}/{filename}
        示例: image/a1/a1b2c3d4.../photo.jpg
        """
        return f"{material_type}/{file_hash[:2]}/{file_hash}/{filename}"
