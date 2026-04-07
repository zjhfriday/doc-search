"""
测试 API 上传接口逻辑
"""
import pytest


class TestDetectMaterialType:
    """文件类型检测"""

    def test_detect_image_jpg(self):
        """检测 JPG 图片"""
        from app.api.v1.upload import _detect_material_type
        result = _detect_material_type("photo.jpg")
        assert result.value == "image"

    def test_detect_image_png(self):
        """检测 PNG 图片"""
        from app.api.v1.upload import _detect_material_type
        result = _detect_material_type("screenshot.png")
        assert result.value == "image"

    def test_detect_image_jpeg(self):
        """检测 JPEG"""
        from app.api.v1.upload import _detect_material_type
        result = _detect_material_type("photo.jpeg")
        assert result.value == "image"

    def test_detect_video_mp4(self):
        """检测 MP4 视频"""
        from app.api.v1.upload import _detect_material_type
        result = _detect_material_type("video.mp4")
        assert result.value == "video"

    def test_detect_video_avi(self):
        """检测 AVI 视频"""
        from app.api.v1.upload import _detect_material_type
        result = _detect_material_type("clip.avi")
        assert result.value == "video"

    def test_detect_video_mov(self):
        """检测 MOV 视频"""
        from app.api.v1.upload import _detect_material_type
        result = _detect_material_type("movie.mov")
        assert result.value == "video"

    def test_detect_unsupported_type(self):
        """不支持的文件类型抛异常"""
        from fastapi import HTTPException
        from app.api.v1.upload import _detect_material_type
        with pytest.raises(HTTPException) as exc_info:
            _detect_material_type("document.pdf")
        assert exc_info.value.status_code == 400

    def test_detect_no_extension(self):
        """无扩展名"""
        from fastapi import HTTPException
        from app.api.v1.upload import _detect_material_type
        with pytest.raises(HTTPException):
            _detect_material_type("noext")

    def test_detect_case_insensitive(self):
        """大小写不敏感"""
        from app.api.v1.upload import _detect_material_type
        result = _detect_material_type("PHOTO.JPG")
        assert result.value == "image"

    def test_detect_webp(self):
        """检测 WebP"""
        from app.api.v1.upload import _detect_material_type
        result = _detect_material_type("image.webp")
        assert result.value == "image"
