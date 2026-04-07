"""
检索服务 - 混合检索调度
"""
from typing import Optional, List

from loguru import logger

from app.schemas.search import (
    SearchRequest, SearchResponse, SearchType, SearchResultItem,
)


class SearchService:
    """
    混合检索服务

    根据检索类型自动选择策略:
    - TEXT → ES关键词检索 + Milvus语义检索 → 结果融合
    - IMAGE → CLIP特征提取 → Milvus相似检索
    - FACE → InsightFace特征提取 → Milvus人脸检索
    - VIDEO_FRAME → CLIP帧向量 → Milvus时间轴检索
    """

    async def search(
        self,
        req: SearchRequest,
        current_user=None,
    ) -> SearchResponse:
        """统一检索入口"""

        if req.search_type == SearchType.TEXT:
            return await self._text_search(req, current_user)
        elif req.search_type == SearchType.IMAGE:
            return await self._image_search(req, current_user)
        elif req.search_type == SearchType.FACE:
            return await self._face_search(req, current_user)
        elif req.search_type == SearchType.VIDEO_FRAME:
            return await self._video_frame_search(req, current_user)
        else:
            return SearchResponse(
                total=0, page=req.page, page_size=req.page_size,
                search_type=req.search_type, items=[],
            )

    async def _text_search(self, req: SearchRequest, user) -> SearchResponse:
        """
        文本混合检索:
        1. ES 关键词检索 → 获取候选集A
        2. Chinese-CLIP 文本→向量 → Milvus语义检索 → 获取候选集B
        3. 结果融合 (RRF / 加权) → 去重 → 权限过滤 → 排序
        """
        logger.info(f"文本检索: query={req.query}")

        # TODO: Step 1 - ES 关键词检索
        # es_results = await self._es_keyword_search(req.query, req)

        # TODO: Step 2 - Milvus 语义检索
        # from app.ai.clip_engine import clip_engine
        # text_vector = clip_engine.extract_text_features(req.query)
        # milvus_results = await self._milvus_vector_search(text_vector, req)

        # TODO: Step 3 - 结果融合
        # merged = self._merge_results(es_results, milvus_results)

        # TODO: Step 4 - 权限过滤
        # filtered = self._filter_by_permission(merged, user)

        return SearchResponse(
            total=0, page=req.page, page_size=req.page_size,
            search_type=SearchType.TEXT, query=req.query, items=[],
        )

    async def _image_search(self, req: SearchRequest, user) -> SearchResponse:
        """以图搜图: CLIP特征 → Milvus 相似检索"""
        logger.info("以图搜图检索")
        # TODO: 实现
        return SearchResponse(
            total=0, page=req.page, page_size=req.page_size,
            search_type=SearchType.IMAGE, items=[],
        )

    async def _face_search(self, req: SearchRequest, user) -> SearchResponse:
        """人脸检索: InsightFace特征 → Milvus 人脸检索"""
        logger.info("人脸检索")
        # TODO: 实现
        return SearchResponse(
            total=0, page=req.page, page_size=req.page_size,
            search_type=SearchType.FACE, items=[],
        )

    async def _video_frame_search(self, req: SearchRequest, user) -> SearchResponse:
        """视频帧语义检索: CLIP文本向量 → Milvus 帧向量检索 → 定位时间轴"""
        logger.info(f"视频帧检索: query={req.query}")
        # TODO: 实现
        return SearchResponse(
            total=0, page=req.page, page_size=req.page_size,
            search_type=SearchType.VIDEO_FRAME, query=req.query, items=[],
        )

    @staticmethod
    def _merge_results(
        es_results: List[dict],
        milvus_results: List[dict],
        es_weight: float = 0.3,
        milvus_weight: float = 0.7,
    ) -> List[dict]:
        """
        Reciprocal Rank Fusion (RRF) 结果融合

        将 ES 关键词检索和 Milvus 语义检索结果按权重融合排序
        """
        score_map = {}

        for rank, item in enumerate(es_results):
            mid = item["material_id"]
            score_map[mid] = score_map.get(mid, 0) + es_weight / (rank + 60)

        for rank, item in enumerate(milvus_results):
            mid = item["material_id"]
            score_map[mid] = score_map.get(mid, 0) + milvus_weight / (rank + 60)

        # 按融合分数排序
        sorted_ids = sorted(score_map.keys(), key=lambda x: score_map[x], reverse=True)
        return sorted_ids
