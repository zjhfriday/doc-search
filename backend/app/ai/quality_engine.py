"""
IQA 图片质量评分引擎封装
"""
from typing import Optional

from loguru import logger


class QualityEngine:
    """图片质量评估引擎"""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def _load_model(self):
        if self._initialized:
            return

        try:
            import pyiqa

            self.device = "cuda" if self._check_cuda() else "cpu"
            # MUSIQ: 多尺度图像质量评估，无需参考图
            self.model = pyiqa.create_metric("musiq", device=self.device)
            self._initialized = True
            logger.info(f"✅ IQA 模型加载完成 (device={self.device})")
        except Exception as e:
            logger.error(f"❌ IQA 模型加载失败: {e}")
            raise

    @staticmethod
    def _check_cuda() -> bool:
        try:
            import torch
            return torch.cuda.is_available()
        except ImportError:
            return False

    def score(self, image_path: str) -> float:
        """
        对图片进行质量评分

        Args:
            image_path: 图片路径

        Returns:
            质量分数 (0-100)，越高越好
        """
        self._load_model()

        try:
            raw_score = float(self.model(image_path).item())
            # MUSIQ 原始分数范围约 0-100
            score = max(0.0, min(100.0, raw_score))
            logger.debug(f"质量评分 {score:.1f}: {image_path}")
            return round(score, 1)
        except Exception as e:
            logger.error(f"质量评分失败 {image_path}: {e}")
            return 0.0

    def is_high_quality(self, image_path: str, threshold: float = 60.0) -> bool:
        """判断图片是否为高质量"""
        return self.score(image_path) >= threshold


# 全局单例
quality_engine = QualityEngine()
