"""
PaddleOCR 文字识别引擎封装
"""
from typing import List, Dict
from loguru import logger

from app.core.config import get_settings

settings = get_settings()


class OCREngine:
    """PaddleOCR 文字识别引擎"""

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
            from paddleocr import PaddleOCR

            self.ocr = PaddleOCR(
                use_angle_cls=True,
                lang=settings.PADDLEOCR_LANG,
                show_log=False,
                use_gpu=self._check_gpu(),
            )
            self._initialized = True
            logger.info("✅ PaddleOCR 模型加载完成")
        except Exception as e:
            logger.error(f"❌ PaddleOCR 模型加载失败: {e}")
            raise

    @staticmethod
    def _check_gpu() -> bool:
        try:
            import paddle
            return paddle.is_compiled_with_cuda()
        except Exception:
            return False

    def extract_text(self, image_path: str) -> str:
        """
        从图片中提取文字

        Args:
            image_path: 图片路径

        Returns:
            识别出的完整文本
        """
        self._load_model()

        result = self.ocr.ocr(image_path, cls=True)
        if not result or not result[0]:
            return ""

        texts = []
        for line in result[0]:
            if line and len(line) >= 2:
                text = line[1][0]  # 文字内容
                confidence = line[1][1]  # 置信度
                if confidence > 0.5:
                    texts.append(text)

        full_text = "\n".join(texts)
        logger.info(f"OCR 提取 {len(texts)} 行文字: {image_path}")
        return full_text

    def extract_text_with_positions(self, image_path: str) -> List[Dict]:
        """
        提取文字及其位置信息

        Returns:
            [{"text": "xxx", "confidence": 0.99, "box": [[x1,y1],[x2,y2],...]}]
        """
        self._load_model()

        result = self.ocr.ocr(image_path, cls=True)
        if not result or not result[0]:
            return []

        items = []
        for line in result[0]:
            if line and len(line) >= 2:
                items.append({
                    "text": line[1][0],
                    "confidence": float(line[1][1]),
                    "box": line[0],
                })

        return items


# 全局单例
ocr_engine = OCREngine()
