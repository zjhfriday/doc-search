"""
InsightFace 人脸引擎封装
- 人脸检测
- 人脸特征提取（用于人脸检索）
- 人脸属性分析（表情、年龄、性别）
"""
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

import numpy as np
from loguru import logger

from app.core.config import get_settings

settings = get_settings()


@dataclass
class FaceResult:
    """单个人脸检测结果"""
    bbox: List[int]               # [x, y, w, h]
    confidence: float             # 检测置信度
    embedding: np.ndarray         # 512维特征向量
    age: Optional[int] = None
    gender: Optional[str] = None  # "M" or "F"
    expression: Optional[str] = None


class FaceEngine:
    """InsightFace 人脸分析引擎"""

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
            from insightface.app import FaceAnalysis

            self.app = FaceAnalysis(
                name=settings.INSIGHTFACE_MODEL,
                root="./models/insightface",
                providers=["CUDAExecutionProvider", "CPUExecutionProvider"],
            )
            self.app.prepare(ctx_id=0, det_size=(640, 640))
            self._initialized = True
            logger.info("✅ InsightFace 模型加载完成")
        except Exception as e:
            logger.error(f"❌ InsightFace 模型加载失败: {e}")
            raise

    def detect_faces(self, image_path: str) -> List[FaceResult]:
        """
        检测图片中的所有人脸并提取特征

        Args:
            image_path: 图片路径

        Returns:
            人脸检测结果列表
        """
        self._load_model()

        import cv2
        img = cv2.imread(image_path)
        if img is None:
            logger.warning(f"无法读取图片: {image_path}")
            return []

        faces = self.app.get(img)

        results = []
        for face in faces:
            bbox = face.bbox.astype(int).tolist()
            result = FaceResult(
                bbox=[bbox[0], bbox[1], bbox[2] - bbox[0], bbox[3] - bbox[1]],
                confidence=float(face.det_score),
                embedding=face.normed_embedding,
                age=int(face.age) if hasattr(face, "age") else None,
                gender="M" if hasattr(face, "gender") and face.gender == 1 else "F",
            )
            results.append(result)

        logger.info(f"检测到 {len(results)} 个人脸: {image_path}")
        return results

    def extract_face_embedding(self, image_path: str) -> Optional[np.ndarray]:
        """
        提取图片中最大人脸的特征向量（用于人脸检索）

        Returns:
            512维特征向量，若无人脸则返回 None
        """
        faces = self.detect_faces(image_path)
        if not faces:
            return None

        # 返回面积最大的人脸
        largest_face = max(faces, key=lambda f: f.bbox[2] * f.bbox[3])
        return largest_face.embedding

    def compare_faces(
        self, embedding1: np.ndarray, embedding2: np.ndarray
    ) -> float:
        """计算两个人脸的相似度 (余弦相似度)"""
        return float(np.dot(embedding1, embedding2))


# 全局单例
face_engine = FaceEngine()
