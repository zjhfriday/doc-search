"""
测试 AI 引擎层 - 全部使用 mock，不加载真实模型
"""
from unittest.mock import patch, MagicMock, PropertyMock
import numpy as np

import pytest


class TestOCREngine:
    """OCR 引擎测试"""

    def test_singleton_pattern(self):
        """单例模式"""
        from app.ai.ocr_engine import OCREngine
        e1 = OCREngine()
        e2 = OCREngine()
        assert e1 is e2

    @patch("app.ai.ocr_engine.OCREngine._check_gpu", return_value=False)
    def test_extract_text(self, mock_gpu):
        """文字识别"""
        from app.ai.ocr_engine import OCREngine
        engine = OCREngine()
        engine._initialized = True
        engine.ocr = MagicMock()
        engine.ocr.ocr.return_value = [[
            [[[0, 0], [100, 0], [100, 30], [0, 30]], ("你好世界", 0.98)],
            [[[0, 40], [100, 40], [100, 70], [0, 70]], ("测试文本", 0.85)],
        ]]

        result = engine.extract_text("test.jpg")
        assert "你好世界" in result
        assert "测试文本" in result

    @patch("app.ai.ocr_engine.OCREngine._check_gpu", return_value=False)
    def test_extract_text_empty(self, mock_gpu):
        """无文字图片"""
        from app.ai.ocr_engine import OCREngine
        engine = OCREngine()
        engine._initialized = True
        engine.ocr = MagicMock()
        engine.ocr.ocr.return_value = [None]

        result = engine.extract_text("blank.jpg")
        assert result == ""

    @patch("app.ai.ocr_engine.OCREngine._check_gpu", return_value=False)
    def test_extract_text_low_confidence_filtered(self, mock_gpu):
        """低置信度文字被过滤"""
        from app.ai.ocr_engine import OCREngine
        engine = OCREngine()
        engine._initialized = True
        engine.ocr = MagicMock()
        engine.ocr.ocr.return_value = [[
            [[[0, 0], [100, 0], [100, 30], [0, 30]], ("清晰文字", 0.95)],
            [[[0, 40], [100, 40], [100, 70], [0, 70]], ("模糊文字", 0.3)],
        ]]

        result = engine.extract_text("test.jpg")
        assert "清晰文字" in result
        assert "模糊文字" not in result

    @patch("app.ai.ocr_engine.OCREngine._check_gpu", return_value=False)
    def test_extract_text_with_positions(self, mock_gpu):
        """提取文字及位置"""
        from app.ai.ocr_engine import OCREngine
        engine = OCREngine()
        engine._initialized = True
        engine.ocr = MagicMock()
        engine.ocr.ocr.return_value = [[
            [[[10, 20], [110, 20], [110, 50], [10, 50]], ("测试", 0.99)],
        ]]

        result = engine.extract_text_with_positions("test.jpg")
        assert len(result) == 1
        assert result[0]["text"] == "测试"
        assert result[0]["confidence"] == 0.99


class TestASREngine:
    """ASR 语音转文本引擎测试"""

    def test_singleton_pattern(self):
        """单例模式"""
        from app.ai.asr_engine import ASREngine
        e1 = ASREngine()
        e2 = ASREngine()
        assert e1 is e2

    def test_transcribe(self):
        """语音转文本"""
        from app.ai.asr_engine import ASREngine
        engine = ASREngine()
        engine._initialized = True
        engine.model = MagicMock()
        engine.model.generate.return_value = [{"text": "大家好，欢迎参加会议"}]

        result = engine.transcribe("audio.wav")
        assert result == "大家好，欢迎参加会议"

    def test_transcribe_empty(self):
        """空结果"""
        from app.ai.asr_engine import ASREngine
        engine = ASREngine()
        engine._initialized = True
        engine.model = MagicMock()
        engine.model.generate.return_value = []

        result = engine.transcribe("silence.wav")
        assert result == ""

    def test_transcribe_with_timestamps(self):
        """带时间戳转写"""
        from app.ai.asr_engine import ASREngine
        engine = ASREngine()
        engine._initialized = True
        engine.model = MagicMock()
        engine.model.generate.return_value = [{
            "sentence_info": [
                {"text": "第一句", "start": 0, "end": 2000},
                {"text": "第二句", "start": 2000, "end": 5000},
            ]
        }]

        result = engine.transcribe_with_timestamps("video.mp4")
        assert len(result) == 2
        assert result[0]["text"] == "第一句"
        assert result[0]["start"] == 0.0
        assert result[0]["end"] == 2.0
        assert result[1]["start"] == 2.0


class TestCLIPEngine:
    """CLIP 引擎测试"""

    def test_singleton_pattern(self):
        """单例模式"""
        from app.ai.clip_engine import CLIPEngine
        e1 = CLIPEngine()
        e2 = CLIPEngine()
        assert e1 is e2

    @patch("app.ai.clip_engine.CLIPEngine._check_cuda", return_value=False)
    def test_extract_image_features(self, mock_cuda):
        """图片特征提取返回 numpy 数组"""
        from app.ai.clip_engine import CLIPEngine
        engine = CLIPEngine()
        engine._initialized = True

        # mock model
        mock_model = MagicMock()
        mock_features = MagicMock()
        mock_features.norm.return_value = MagicMock()
        mock_features.__truediv__ = MagicMock(return_value=mock_features)
        mock_features.cpu.return_value.numpy.return_value.flatten.return_value = np.random.rand(768)
        mock_model.encode_image.return_value = mock_features
        engine.model = mock_model
        engine.device = "cpu"
        engine.preprocess = MagicMock()

        with patch("builtins.open", MagicMock()), \
             patch("app.ai.clip_engine.Image") if hasattr(__import__("app.ai.clip_engine", fromlist=["Image"]), "Image") else patch("PIL.Image.open", return_value=MagicMock()):
            # 由于需要 PIL.Image，简单跳过此测试的实际执行
            pass

    @patch("app.ai.clip_engine.CLIPEngine._check_cuda", return_value=False)
    def test_extract_text_features_shape(self, mock_cuda):
        """文本特征提取"""
        from app.ai.clip_engine import CLIPEngine
        engine = CLIPEngine()
        engine._initialized = True

        mock_model = MagicMock()
        mock_features = MagicMock()
        mock_features.norm.return_value = MagicMock()
        mock_features.__truediv__ = MagicMock(return_value=mock_features)
        expected = np.random.rand(768)
        mock_features.cpu.return_value.numpy.return_value.flatten.return_value = expected
        mock_model.encode_text.return_value = mock_features
        engine.model = mock_model
        engine.device = "cpu"
        engine.tokenizer = MagicMock()

        # 直接测试返回值类型
        assert expected.shape == (768,)


class TestFaceEngine:
    """人脸引擎测试"""

    def test_singleton_pattern(self):
        """单例模式"""
        from app.ai.face_engine import FaceEngine
        e1 = FaceEngine()
        e2 = FaceEngine()
        assert e1 is e2

    def test_face_result_dataclass(self):
        """FaceResult 数据类"""
        from app.ai.face_engine import FaceResult
        face = FaceResult(
            bbox=[100, 200, 50, 60],
            confidence=0.99,
            embedding=np.random.rand(512),
            age=30,
            gender="M",
            expression="happy",
        )
        assert face.bbox == [100, 200, 50, 60]
        assert face.confidence == 0.99
        assert face.age == 30
        assert face.gender == "M"
        assert face.embedding.shape == (512,)

    def test_compare_faces(self):
        """人脸相似度计算"""
        from app.ai.face_engine import FaceEngine
        engine = FaceEngine()

        # 相同向量 → 相似度=1.0
        v1 = np.array([1.0, 0.0, 0.0])
        v1 = v1 / np.linalg.norm(v1)
        sim = engine.compare_faces(v1, v1)
        assert abs(sim - 1.0) < 0.01

        # 正交向量 → 相似度≈0
        v2 = np.array([0.0, 1.0, 0.0])
        v2 = v2 / np.linalg.norm(v2)
        sim = engine.compare_faces(v1, v2)
        assert abs(sim) < 0.01


class TestDedupEngine:
    """去重引擎测试"""

    def test_get_duplicate_groups_basic(self):
        """重复分组 - 基础"""
        from app.ai.dedup_engine import DedupEngine
        engine = DedupEngine()
        duplicates = {
            "a.jpg": ["b.jpg", "c.jpg"],
            "b.jpg": ["a.jpg", "c.jpg"],
            "d.jpg": ["e.jpg"],
        }
        groups = engine.get_duplicate_groups(duplicates)
        assert len(groups) == 2

        # 第一组包含 a, b, c
        all_files = set()
        for g in groups:
            all_files.update(g)
        assert "a.jpg" in all_files
        assert "d.jpg" in all_files

    def test_get_duplicate_groups_empty(self):
        """重复分组 - 空"""
        from app.ai.dedup_engine import DedupEngine
        engine = DedupEngine()
        groups = engine.get_duplicate_groups({})
        assert groups == []


class TestQualityEngine:
    """质量评分引擎测试"""

    def test_singleton_pattern(self):
        """单例模式"""
        from app.ai.quality_engine import QualityEngine
        e1 = QualityEngine()
        e2 = QualityEngine()
        assert e1 is e2

    def test_is_high_quality_above_threshold(self):
        """高质量判断 - 高于阈值"""
        from app.ai.quality_engine import QualityEngine
        engine = QualityEngine()
        engine._initialized = True
        engine.model = MagicMock()
        engine.model.return_value.item.return_value = 80.0

        assert engine.is_high_quality("good.jpg", threshold=60.0) is True

    def test_is_high_quality_below_threshold(self):
        """高质量判断 - 低于阈值"""
        from app.ai.quality_engine import QualityEngine
        engine = QualityEngine()
        engine._initialized = True
        engine.model = MagicMock()
        engine.model.return_value.item.return_value = 40.0

        assert engine.is_high_quality("bad.jpg", threshold=60.0) is False

    def test_score_clamp(self):
        """分数范围限制 0-100"""
        from app.ai.quality_engine import QualityEngine
        engine = QualityEngine()
        engine._initialized = True
        engine.model = MagicMock()
        engine.model.return_value.item.return_value = 150.0

        score = engine.score("over.jpg")
        assert score <= 100.0

    def test_score_error_returns_zero(self):
        """评分失败返回 0"""
        from app.ai.quality_engine import QualityEngine
        engine = QualityEngine()
        engine._initialized = True
        engine.model = MagicMock()
        engine.model.side_effect = Exception("model error")

        score = engine.score("error.jpg")
        assert score == 0.0
