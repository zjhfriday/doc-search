"""
Chinese-CLIP 引擎封装
- 图片 → 特征向量
- 文本 → 特征向量
- 用于语义检索和以图搜图
"""
from typing import List, Union
from pathlib import Path

import numpy as np
from loguru import logger

from app.core.config import get_settings

settings = get_settings()


class CLIPEngine:
    """Chinese-CLIP 特征提取引擎"""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def _load_model(self):
        """懒加载模型"""
        if self._initialized:
            return

        try:
            import cn_clip.clip as clip
            from cn_clip.clip import load_from_name

            self.device = "cuda" if self._check_cuda() else "cpu"
            self.model, self.preprocess = load_from_name(
                settings.CLIP_MODEL_NAME,
                device=self.device,
                download_root="./models/clip",
            )
            self.tokenizer = clip.tokenize
            self._initialized = True
            logger.info(f"✅ Chinese-CLIP 模型加载完成 (device={self.device})")
        except Exception as e:
            logger.error(f"❌ Chinese-CLIP 模型加载失败: {e}")
            raise

    @staticmethod
    def _check_cuda() -> bool:
        try:
            import torch
            return torch.cuda.is_available()
        except ImportError:
            return False

    def extract_image_features(self, image_path: str) -> np.ndarray:
        """
        提取图片的 CLIP 特征向量

        Args:
            image_path: 图片文件路径

        Returns:
            归一化后的特征向量 (768维)
        """
        self._load_model()

        import torch
        from PIL import Image

        image = Image.open(image_path).convert("RGB")
        image_input = self.preprocess(image).unsqueeze(0).to(self.device)

        with torch.no_grad():
            features = self.model.encode_image(image_input)
            features = features / features.norm(dim=-1, keepdim=True)

        return features.cpu().numpy().flatten()

    def extract_text_features(self, text: str) -> np.ndarray:
        """
        提取文本的 CLIP 特征向量

        Args:
            text: 检索文本

        Returns:
            归一化后的特征向量 (768维)
        """
        self._load_model()

        import torch

        text_input = self.tokenizer([text]).to(self.device)

        with torch.no_grad():
            features = self.model.encode_text(text_input)
            features = features / features.norm(dim=-1, keepdim=True)

        return features.cpu().numpy().flatten()

    def extract_batch_image_features(
        self, image_paths: List[str], batch_size: int = 32
    ) -> List[np.ndarray]:
        """批量提取图片特征向量"""
        self._load_model()

        import torch
        from PIL import Image

        all_features = []

        for i in range(0, len(image_paths), batch_size):
            batch_paths = image_paths[i : i + batch_size]
            images = []
            for p in batch_paths:
                try:
                    img = Image.open(p).convert("RGB")
                    images.append(self.preprocess(img))
                except Exception as e:
                    logger.warning(f"图片加载失败 {p}: {e}")
                    images.append(torch.zeros(3, 224, 224))  # placeholder

            image_input = torch.stack(images).to(self.device)

            with torch.no_grad():
                features = self.model.encode_image(image_input)
                features = features / features.norm(dim=-1, keepdim=True)

            all_features.extend(features.cpu().numpy())

        return all_features


# 全局单例
clip_engine = CLIPEngine()
