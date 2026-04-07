"""
PySceneDetect 视频场景检测与关键帧提取
"""
from typing import List, Tuple
from pathlib import Path

from loguru import logger


class SceneDetectEngine:
    """视频场景检测与抽帧引擎"""

    def extract_keyframes(
        self,
        video_path: str,
        output_dir: str,
        threshold: float = 27.0,
        max_frames: int = 50,
    ) -> List[dict]:
        """
        从视频中提取关键帧

        Args:
            video_path: 视频文件路径
            output_dir: 关键帧输出目录
            threshold: 场景切换阈值（越小越敏感）
            max_frames: 最大提取帧数

        Returns:
            [{"frame_path": "xxx.jpg", "timestamp": 10.5, "scene_index": 0}]
        """
        try:
            from scenedetect import detect, ContentDetector, AdaptiveDetector
            from scenedetect import open_video, SceneManager
            import cv2

            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)

            # 检测场景
            video = open_video(video_path)
            scene_manager = SceneManager()
            scene_manager.add_detector(ContentDetector(threshold=threshold))
            scene_manager.detect_scenes(video)
            scene_list = scene_manager.get_scene_list()

            if not scene_list:
                # 无场景切换时，按固定间隔抽帧
                return self._extract_uniform_frames(video_path, output_dir, max_frames)

            # 每个场景取中间帧
            keyframes = []
            cap = cv2.VideoCapture(video_path)
            fps = cap.get(cv2.CAP_PROP_FPS) or 25.0

            for idx, (start, end) in enumerate(scene_list[:max_frames]):
                mid_frame = (start.get_frames() + end.get_frames()) // 2
                timestamp = mid_frame / fps

                cap.set(cv2.CAP_PROP_POS_FRAMES, mid_frame)
                ret, frame = cap.read()
                if ret:
                    frame_filename = f"keyframe_{idx:04d}_{mid_frame}.jpg"
                    frame_path = str(output_path / frame_filename)
                    cv2.imwrite(frame_path, frame)

                    keyframes.append({
                        "frame_path": frame_path,
                        "timestamp": round(timestamp, 2),
                        "scene_index": idx,
                        "frame_number": mid_frame,
                    })

            cap.release()
            logger.info(f"提取 {len(keyframes)} 个关键帧: {video_path}")
            return keyframes

        except Exception as e:
            logger.error(f"关键帧提取失败 {video_path}: {e}")
            return []

    def _extract_uniform_frames(
        self, video_path: str, output_dir: str, max_frames: int = 20
    ) -> List[dict]:
        """按均匀间隔提取帧（无场景切换时的兜底方案）"""
        import cv2

        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        cap = cv2.VideoCapture(video_path)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
        interval = max(total_frames // max_frames, 1)

        keyframes = []
        for idx in range(0, total_frames, interval):
            if len(keyframes) >= max_frames:
                break

            cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
            ret, frame = cap.read()
            if ret:
                frame_filename = f"uniform_{idx:06d}.jpg"
                frame_path = str(output_path / frame_filename)
                cv2.imwrite(frame_path, frame)

                keyframes.append({
                    "frame_path": frame_path,
                    "timestamp": round(idx / fps, 2),
                    "scene_index": len(keyframes),
                    "frame_number": idx,
                })

        cap.release()
        return keyframes


# 全局单例
scene_detect_engine = SceneDetectEngine()
