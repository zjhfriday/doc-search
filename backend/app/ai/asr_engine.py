"""
FunASR 语音转文本引擎封装
- 视频/音频文件 → 文本
"""
from typing import Optional, List, Dict
from loguru import logger

from app.core.config import get_settings

settings = get_settings()


class ASREngine:
    """FunASR 语音识别引擎"""

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
            from funasr import AutoModel

            self.model = AutoModel(
                model=settings.ASR_MODEL,
                vad_model="fsmn-vad",
                punc_model="ct-punc",
                log_level="ERROR",
            )
            self._initialized = True
            logger.info("✅ FunASR 模型加载完成")
        except Exception as e:
            logger.error(f"❌ FunASR 模型加载失败: {e}")
            raise

    def transcribe(self, audio_path: str) -> str:
        """
        将音频/视频文件转写为文本

        Args:
            audio_path: 音频或视频文件路径

        Returns:
            转写文本
        """
        self._load_model()

        try:
            result = self.model.generate(input=audio_path)
            if result and len(result) > 0:
                text = result[0].get("text", "")
                logger.info(f"ASR 转写完成，文本长度: {len(text)}, 文件: {audio_path}")
                return text
        except Exception as e:
            logger.error(f"ASR 转写失败 {audio_path}: {e}")

        return ""

    def transcribe_with_timestamps(self, audio_path: str) -> List[Dict]:
        """
        转写并返回时间戳信息

        Returns:
            [{"text": "xxx", "start": 0.0, "end": 2.5}]
        """
        self._load_model()

        try:
            result = self.model.generate(
                input=audio_path,
                output_timestamp=True,
            )
            if result and len(result) > 0:
                # FunASR 返回的时间戳格式
                segments = result[0].get("sentence_info", [])
                return [
                    {
                        "text": seg.get("text", ""),
                        "start": seg.get("start", 0) / 1000.0,  # ms → s
                        "end": seg.get("end", 0) / 1000.0,
                    }
                    for seg in segments
                ]
        except Exception as e:
            logger.error(f"ASR 带时间戳转写失败 {audio_path}: {e}")

        return []


# 全局单例
asr_engine = ASREngine()
