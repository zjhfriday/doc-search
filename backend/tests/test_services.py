"""
测试 Services 层 - 业务逻辑
"""
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timezone

import pytest


class TestSearchService:
    """检索服务测试"""

    @pytest.mark.asyncio
    async def test_text_search_returns_response(self):
        """文本检索返回正确结构"""
        from app.services.search_service import SearchService
        from app.schemas.search import SearchRequest, SearchType

        service = SearchService()
        req = SearchRequest(query="表彰大会", search_type=SearchType.TEXT)
        result = await service.search(req)

        assert result.search_type == SearchType.TEXT
        assert result.query == "表彰大会"
        assert result.total == 0
        assert isinstance(result.items, list)

    @pytest.mark.asyncio
    async def test_image_search_returns_response(self):
        """以图搜图返回正确结构"""
        from app.services.search_service import SearchService
        from app.schemas.search import SearchRequest, SearchType

        service = SearchService()
        req = SearchRequest(search_type=SearchType.IMAGE, page=1, page_size=10)
        result = await service.search(req)

        assert result.search_type == SearchType.IMAGE
        assert result.page == 1

    @pytest.mark.asyncio
    async def test_face_search_returns_response(self):
        """人脸检索返回正确结构"""
        from app.services.search_service import SearchService
        from app.schemas.search import SearchRequest, SearchType

        service = SearchService()
        req = SearchRequest(search_type=SearchType.FACE)
        result = await service.search(req)

        assert result.search_type == SearchType.FACE

    @pytest.mark.asyncio
    async def test_video_frame_search_returns_response(self):
        """视频帧检索返回正确结构"""
        from app.services.search_service import SearchService
        from app.schemas.search import SearchRequest, SearchType

        service = SearchService()
        req = SearchRequest(query="领导讲话", search_type=SearchType.VIDEO_FRAME)
        result = await service.search(req)

        assert result.search_type == SearchType.VIDEO_FRAME
        assert result.query == "领导讲话"

    def test_merge_results_rrf(self):
        """RRF 结果融合"""
        from app.services.search_service import SearchService

        es_results = [
            {"material_id": 1}, {"material_id": 2}, {"material_id": 3},
        ]
        milvus_results = [
            {"material_id": 2}, {"material_id": 4}, {"material_id": 1},
        ]

        merged = SearchService._merge_results(es_results, milvus_results)
        assert isinstance(merged, list)
        # material_id=2 在两个结果中都出现，应该排在前面
        assert 2 in merged
        assert 1 in merged

    def test_merge_results_empty(self):
        """空结果融合"""
        from app.services.search_service import SearchService
        merged = SearchService._merge_results([], [])
        assert merged == []


class TestUploadService:
    """上传服务测试"""

    def test_generate_object_path(self):
        """对象路径生成"""
        from app.services.upload_service import UploadService
        path = UploadService.generate_object_path(
            material_type="image",
            file_hash="abcdef1234567890",
            filename="photo.jpg",
        )
        assert path == "image/ab/abcdef1234567890/photo.jpg"

    def test_generate_object_path_video(self):
        """视频对象路径"""
        from app.services.upload_service import UploadService
        path = UploadService.generate_object_path(
            material_type="video",
            file_hash="ff0011223344",
            filename="clip.mp4",
        )
        assert path.startswith("video/ff/")
        assert "clip.mp4" in path


class TestGovernanceService:
    """治理服务测试"""

    @pytest.mark.asyncio
    async def test_get_storage_stats(self):
        """存储统计"""
        from app.services.governance_service import GovernanceService

        mock_db = AsyncMock()
        # mock total_size
        mock_db.execute = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar.return_value = 1073741824  # 1 GB

        mock_db.execute.return_value = mock_result

        service = GovernanceService(mock_db)

        # 需要三次调用 execute，分别返回不同值
        mock_db.execute.side_effect = [
            MagicMock(scalar=MagicMock(return_value=1073741824)),  # total_size
            MagicMock(scalar=MagicMock(return_value=100)),          # total_count
            MagicMock(scalar=MagicMock(return_value=5)),            # duplicate_count
        ]

        stats = await service.get_storage_stats()
        assert stats["total_count"] == 100
        assert stats["total_size_bytes"] == 1073741824
        assert stats["total_size_gb"] == 1.0
        assert stats["duplicate_count"] == 5
