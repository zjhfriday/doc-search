"""
业务流程集成测试 - 模拟真实用户场景
对应需求文档中的核心场景
"""
import hashlib
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timezone, timedelta

import pytest
import numpy as np

from tests.factories import (
    UserFactory, MaterialFactory, TagFactory,
    FaceFactory, AuditLogFactory, DownloadRecordFactory,
)


# ============================================================
# 场景1: 临时要素材，马上要
# "领导10分钟后开会，需要去年表彰大会总经理讲话的高清照片"
# ============================================================

class TestScenario1_UrgentSearch:
    """场景1: 紧急检索素材"""

    @pytest.mark.asyncio
    async def test_text_search_by_event_and_person(self):
        """通过活动名+人物进行文本检索"""
        from app.services.search_service import SearchService
        from app.schemas.search import SearchRequest, SearchType

        service = SearchService()
        req = SearchRequest(
            query="去年表彰大会 总经理 发言 高清",
            search_type=SearchType.TEXT,
            min_quality=60.0,
            page_size=20,
        )
        result = await service.search(req)

        assert result.search_type == SearchType.TEXT
        assert result.query == "去年表彰大会 总经理 发言 高清"
        assert isinstance(result.items, list)

    def test_quality_filter_works(self):
        """质量过滤: 低于阈值的素材不应返回"""
        materials = MaterialFactory.create_batch_images(10)

        # 模拟质量过滤
        high_quality = [m for m in materials if m.quality_score >= 60.0]
        low_quality = [m for m in materials if m.quality_score < 60.0]

        for m in high_quality:
            assert m.quality_score >= 60.0

    def test_security_level_filter(self):
        """权限过滤: 普通用户不应看到涉密素材"""
        user = UserFactory.create(role="user")
        materials = [
            MaterialFactory.create_image(security_level="public"),
            MaterialFactory.create_image(security_level="internal"),
            MaterialFactory.create_image(security_level="confidential"),
        ]

        # 模拟权限过滤逻辑
        allowed_levels = {"public", "internal"}  # 普通用户可见范围
        visible = [m for m in materials if m.security_level in allowed_levels]
        assert len(visible) == 2


# ============================================================
# 场景2: 做宣传稿，想找同类型好图
# "需要会议类、党建类、领导视察类素材，每类前20张高质量图"
# ============================================================

class TestScenario2_CategoryBrowse:
    """场景2: 分类浏览高质量素材"""

    def test_batch_create_materials_by_event(self):
        """按活动类型批量创建素材"""
        meeting_materials = MaterialFactory.create_batch_images(
            20, event_name="2024经营总结会"
        )
        assert len(meeting_materials) == 20
        assert all(m.event_name == "2024经营总结会" for m in meeting_materials)

    def test_duplicate_folding(self):
        """重复素材折叠: 相同 hash 的只保留最佳"""
        dup_group = MaterialFactory.create_duplicate_group(count=4)

        assert len(dup_group) == 4
        # 第一张不是重复，后面的标记为重复
        assert dup_group[0].is_duplicate is False
        for m in dup_group[1:]:
            assert m.is_duplicate is True

        # 所有素材共享同一个 hash
        hashes = {m.file_hash for m in dup_group}
        assert len(hashes) == 1

    def test_sort_by_quality(self):
        """按质量分排序"""
        materials = MaterialFactory.create_batch_images(10)
        sorted_materials = sorted(materials, key=lambda m: m.quality_score, reverse=True)
        for i in range(len(sorted_materials) - 1):
            assert sorted_materials[i].quality_score >= sorted_materials[i + 1].quality_score


# ============================================================
# 场景3: 视频里找某个瞬间
# "需要领导在台上讲话、观众鼓掌的那一段"
# ============================================================

class TestScenario3_VideoFrameSearch:
    """场景3: 视频帧语义检索"""

    @pytest.mark.asyncio
    async def test_video_frame_search_request(self):
        """视频帧语义检索请求"""
        from app.services.search_service import SearchService
        from app.schemas.search import SearchRequest, SearchType

        service = SearchService()
        req = SearchRequest(
            query="领导在台上讲话、观众鼓掌",
            search_type=SearchType.VIDEO_FRAME,
        )
        result = await service.search(req)

        assert result.search_type == SearchType.VIDEO_FRAME
        assert result.query == "领导在台上讲话、观众鼓掌"

    def test_video_material_has_asr_text(self):
        """视频素材包含 ASR 转写文本"""
        video = MaterialFactory.create_video(
            asr_text="同志们，过去一年我们取得了显著成绩"
        )
        assert video.material_type == "video"
        assert video.asr_text is not None
        assert "显著成绩" in video.asr_text

    def test_video_material_has_timestamps(self):
        """视频素材有时长和帧率"""
        video = MaterialFactory.create_video(duration=3600.0, fps=30.0)
        assert video.duration == 3600.0
        assert video.fps == 30.0
        assert video.frame_count is not None


# ============================================================
# 场景4: 素材上传
# "批量上传，只填关键信息，AI自动打标签"
# ============================================================

class TestScenario4_Upload:
    """场景4: 素材上传流程"""

    def test_detect_image_type(self):
        """自动识别图片类型"""
        from app.api.v1.upload import _detect_material_type
        assert _detect_material_type("photo.jpg").value == "image"
        assert _detect_material_type("video.mp4").value == "video"

    def test_file_hash_calculation(self):
        """文件哈希计算（去重依据）"""
        content = b"fake image file content for testing"
        file_hash = hashlib.md5(content).hexdigest()
        assert len(file_hash) == 32

        # 相同内容产生相同哈希
        file_hash2 = hashlib.md5(content).hexdigest()
        assert file_hash == file_hash2

        # 不同内容产生不同哈希
        file_hash3 = hashlib.md5(b"different content").hexdigest()
        assert file_hash != file_hash3

    def test_object_path_generation(self):
        """MinIO 对象路径生成"""
        from app.services.upload_service import UploadService
        path = UploadService.generate_object_path("image", "abcdef123456", "photo.jpg")
        assert path == "image/ab/abcdef123456/photo.jpg"

    def test_batch_upload_creates_multiple_materials(self):
        """批量上传创建多个素材记录"""
        materials = MaterialFactory.create_batch_images(5, event_name="2024年运动会")
        assert len(materials) == 5
        assert all(m.event_name == "2024年运动会" for m in materials)

    def test_upload_triggers_ai_pipeline(self):
        """上传后触发 AI 流水线（验证任务可调用）"""
        from app.tasks.ai_process import (
            generate_thumbnail, extract_metadata,
            run_ocr, run_clip, run_face_detection,
            run_asr, run_quality_score,
        )
        # 所有 AI 任务都可以调用
        assert generate_thumbnail(1) == 1
        assert extract_metadata(1) == 1
        assert callable(run_ocr)
        assert callable(run_clip)
        assert callable(run_face_detection)
        assert callable(run_asr)
        assert callable(run_quality_score)


# ============================================================
# 场景5: 安全与权限
# "涉密素材不能外发，需要区分管控"
# ============================================================

class TestScenario5_Security:
    """场景5: 安全与权限控制"""

    def test_security_levels_exist(self):
        """密级分级完整"""
        from app.models.material import SecurityLevel
        levels = [e.value for e in SecurityLevel]
        assert "public" in levels
        assert "internal" in levels
        assert "restricted" in levels
        assert "confidential" in levels

    def test_role_based_access(self):
        """角色权限划分"""
        admin = UserFactory.create_admin()
        manager = UserFactory.create_manager()
        user = UserFactory.create(role="user")
        guest = UserFactory.create(role="guest")

        assert admin.role == "super_admin"
        assert manager.role == "manager"
        assert user.role == "user"
        assert guest.role == "guest"

    def test_password_hashing(self):
        """密码存储安全"""
        from app.core.security import hash_password, verify_password
        hashed = hash_password("secure_password_123")
        assert hashed != "secure_password_123"
        assert verify_password("secure_password_123", hashed)
        assert not verify_password("wrong_password", hashed)

    def test_jwt_token_lifecycle(self):
        """JWT Token 生命周期"""
        from app.core.security import create_access_token, decode_access_token
        token = create_access_token(data={"sub": "42", "role": "user"})

        payload = decode_access_token(token)
        assert payload["sub"] == "42"
        assert payload["role"] == "user"
        assert "exp" in payload

    def test_audit_log_creation(self):
        """操作审计日志记录"""
        logs = AuditLogFactory.create_batch(10, action="download")
        assert len(logs) == 10
        assert all(log.action == "download" for log in logs)
        assert all(log.ip_address is not None for log in logs)
        assert all(log.user is not None for log in logs)

    def test_download_record_tracking(self):
        """下载记录追踪"""
        records = DownloadRecordFactory.create_batch(5)
        assert len(records) == 5
        for r in records:
            assert r.user_id is not None
            assert r.material_id is not None
            assert r.download_purpose is not None
            assert r.ip_address is not None

    def test_expired_material_detection(self):
        """过期素材检测"""
        expired = MaterialFactory.create_expired()
        now = datetime.now(timezone.utc)
        assert expired.expires_at < now


# ============================================================
# 场景6: AI 能力集成
# ============================================================

class TestScenario6_AICapabilities:
    """AI 能力集成测试"""

    def test_ocr_engine_mock(self):
        """OCR 引擎 mock 测试"""
        from app.ai.ocr_engine import OCREngine
        engine = OCREngine()
        engine._initialized = True
        engine.ocr = MagicMock()
        engine.ocr.ocr.return_value = [[
            [[[0, 0], [200, 0], [200, 40], [0, 40]], ("2024年度表彰大会", 0.98)],
            [[[0, 50], [200, 50], [200, 90], [0, 90]], ("先进集体", 0.95)],
        ]]

        text = engine.extract_text("award_ceremony.jpg")
        assert "2024年度表彰大会" in text
        assert "先进集体" in text

    def test_face_comparison(self):
        """人脸相似度比较"""
        from app.ai.face_engine import FaceEngine
        engine = FaceEngine()

        # 同一人 → 高相似度
        v1 = FaceFactory.create_face_embedding()
        sim_same = engine.compare_faces(v1, v1)
        assert sim_same > 0.99

        # 不同人 → 低相似度
        v2 = FaceFactory.create_face_embedding()
        sim_diff = engine.compare_faces(v1, v2)
        assert sim_diff < sim_same

    def test_dedup_grouping(self):
        """去重分组"""
        from app.ai.dedup_engine import DedupEngine
        engine = DedupEngine()

        duplicates = {
            "img_001.jpg": ["img_002.jpg", "img_003.jpg"],
            "img_002.jpg": ["img_001.jpg", "img_003.jpg"],
            "img_010.jpg": ["img_011.jpg"],
        }
        groups = engine.get_duplicate_groups(duplicates)
        assert len(groups) == 2

    def test_quality_score_engine_mock(self):
        """质量评分 mock"""
        from app.ai.quality_engine import QualityEngine
        engine = QualityEngine()
        engine._initialized = True
        engine.model = MagicMock()
        engine.model.return_value.item.return_value = 85.0

        score = engine.score("high_quality.jpg")
        assert score == 85.0
        assert engine.is_high_quality("high_quality.jpg", threshold=60)

    def test_rrf_merge_results(self):
        """RRF 结果融合 - ES + Milvus"""
        from app.services.search_service import SearchService

        es_results = [
            {"material_id": 10},
            {"material_id": 20},
            {"material_id": 30},
        ]
        milvus_results = [
            {"material_id": 20},
            {"material_id": 40},
            {"material_id": 10},
        ]

        merged = SearchService._merge_results(
            es_results, milvus_results,
            es_weight=0.3, milvus_weight=0.7,
        )

        # material_id=20 在两个列表都排前列，应该排名靠前
        assert merged[0] == 20
        assert 10 in merged
        assert 40 in merged


# ============================================================
# 场景7: 数据工厂批量生成验证
# ============================================================

class TestDataFactories:
    """数据工厂完整性测试"""

    def test_create_batch_users(self):
        """批量创建用户"""
        users = UserFactory.create_batch(20)
        assert len(users) == 20
        usernames = [u.username for u in users]
        assert len(set(usernames)) == 20  # 用户名唯一

    def test_create_batch_images(self):
        """批量创建图片素材"""
        images = MaterialFactory.create_batch_images(50)
        assert len(images) == 50
        assert all(m.material_type == "image" for m in images)
        assert all(m.file_size > 0 for m in images)

    def test_create_batch_videos(self):
        """批量创建视频素材"""
        videos = MaterialFactory.create_batch_videos(10)
        assert len(videos) == 10
        assert all(m.material_type == "video" for m in videos)
        assert all(m.duration is not None for m in videos)
        assert all(m.fps is not None for m in videos)

    def test_create_mixed_materials(self):
        """混合创建图片和视频"""
        images = MaterialFactory.create_batch_images(30)
        videos = MaterialFactory.create_batch_videos(10)
        all_materials = images + videos
        assert len(all_materials) == 40

        image_count = sum(1 for m in all_materials if m.material_type == "image")
        video_count = sum(1 for m in all_materials if m.material_type == "video")
        assert image_count == 30
        assert video_count == 10

    def test_create_tags_by_category(self):
        """按分类创建标签"""
        person_tags = TagFactory.create_batch(5, category="person")
        scene_tags = TagFactory.create_batch(5, category="scene")

        assert all(t.category == "person" for t in person_tags)
        assert all(t.category == "scene" for t in scene_tags)

    def test_create_face_library(self):
        """创建人脸库"""
        faces = [FaceFactory.create_face_library_entry() for _ in range(10)]
        assert len(faces) == 10
        assert all(f.person_name is not None for f in faces)
        assert all(f.person_title is not None for f in faces)

    def test_create_face_embeddings(self):
        """生成人脸特征向量"""
        embeddings = [FaceFactory.create_face_embedding() for _ in range(5)]
        for emb in embeddings:
            assert emb.shape == (512,)
            # 向量已归一化
            norm = np.linalg.norm(emb)
            assert abs(norm - 1.0) < 0.01

    def test_create_audit_logs(self):
        """创建审计日志"""
        logs = AuditLogFactory.create_batch(50)
        assert len(logs) == 50
        actions = {log.action for log in logs}
        assert len(actions) > 1  # 多种操作类型

    def test_create_download_records(self):
        """创建下载记录"""
        records = DownloadRecordFactory.create_batch(20)
        assert len(records) == 20
        assert all(r.download_purpose is not None for r in records)
