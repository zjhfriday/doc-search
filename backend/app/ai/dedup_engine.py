"""
imagededup 图片去重引擎封装
"""
from typing import Dict, List, Set
from pathlib import Path

from loguru import logger


class DedupEngine:
    """图片去重引擎"""

    def find_duplicates_hash(
        self, image_dir: str, hash_size: int = 8
    ) -> Dict[str, List[str]]:
        """
        使用感知哈希(PHash)查找重复图片

        Args:
            image_dir: 图片目录
            hash_size: 哈希大小（越大越精确）

        Returns:
            {filename: [duplicate_filenames]}
        """
        try:
            from imagededup.methods import PHash

            hasher = PHash()
            encodings = hasher.encode_images(image_dir=image_dir)
            duplicates = hasher.find_duplicates(
                encoding_map=encodings,
                max_distance_threshold=10,
            )

            # 过滤空结果
            result = {k: v for k, v in duplicates.items() if v}
            logger.info(f"PHash 去重: 扫描 {len(encodings)} 张, 发现 {len(result)} 组重复")
            return result

        except Exception as e:
            logger.error(f"PHash 去重失败: {e}")
            return {}

    def find_duplicates_cnn(
        self, image_dir: str, min_similarity: float = 0.9
    ) -> Dict[str, List[str]]:
        """
        使用 CNN 特征查找近似重复图片（更精确但更慢）

        Args:
            image_dir: 图片目录
            min_similarity: 最低相似度阈值

        Returns:
            {filename: [similar_filenames]}
        """
        try:
            from imagededup.methods import CNN

            cnn = CNN()
            encodings = cnn.encode_images(image_dir=image_dir)
            duplicates = cnn.find_duplicates(
                encoding_map=encodings,
                min_similarity_threshold=min_similarity,
            )

            result = {k: v for k, v in duplicates.items() if v}
            logger.info(f"CNN 去重: 扫描 {len(encodings)} 张, 发现 {len(result)} 组近似重复")
            return result

        except Exception as e:
            logger.error(f"CNN 去重失败: {e}")
            return {}

    def get_duplicate_groups(self, duplicates: Dict[str, List[str]]) -> List[Set[str]]:
        """将重复映射转为不重复的分组"""
        visited = set()
        groups = []

        for filename, dups in duplicates.items():
            if filename in visited:
                continue
            group = {filename} | set(dups)
            visited.update(group)
            groups.append(group)

        return groups


# 全局单例
dedup_engine = DedupEngine()
