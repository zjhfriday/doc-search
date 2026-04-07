"""
检索接口 - 文本检索 / 语义检索 / 以图搜图 / 人脸检索 / 视频帧检索
"""
from fastapi import APIRouter, Depends, UploadFile, File, Form
from typing import Optional

from app.core.security import get_current_user
from app.models.user import User
from app.schemas.search import (
    SearchRequest, SearchResponse, SearchType, SearchResultItem,
)

router = APIRouter()


@router.post("", response_model=SearchResponse, summary="统一检索入口")
async def search_materials(
    req: SearchRequest,
    current_user: User = Depends(get_current_user),
):
    """
    统一检索入口，根据 search_type 自动路由:
    - text: 关键词(ES) + 语义(Milvus/CLIP) 混合检索
    - image: 以图搜图（CLIP特征匹配）
    - face: 人脸检索（InsightFace特征匹配）
    - video_frame: 视频帧语义检索
    """
    # TODO: 调用 SearchService 执行检索逻辑
    # from app.services.search_service import SearchService
    # service = SearchService()
    # results = await service.search(req, current_user)

    return SearchResponse(
        total=0,
        page=req.page,
        page_size=req.page_size,
        search_type=req.search_type,
        query=req.query,
        items=[],
    )


@router.post("/by-image", response_model=SearchResponse, summary="以图搜图")
async def search_by_image(
    file: UploadFile = File(..., description="上传图片进行相似检索"),
    page: int = Form(1),
    page_size: int = Form(20),
    current_user: User = Depends(get_current_user),
):
    """
    上传一张图片，检索相似素材
    1. 用 CLIP 提取图片特征向量
    2. 在 Milvus 中进行向量相似度检索
    3. 返回相似素材列表
    """
    # TODO: 实现以图搜图逻辑
    return SearchResponse(
        total=0,
        page=page,
        page_size=page_size,
        search_type=SearchType.IMAGE,
        items=[],
    )


@router.post("/by-face", response_model=SearchResponse, summary="人脸检索")
async def search_by_face(
    file: UploadFile = File(..., description="上传人脸照片进行检索"),
    page: int = Form(1),
    page_size: int = Form(20),
    current_user: User = Depends(get_current_user),
):
    """
    上传一张人脸照片，检索包含该人脸的所有素材
    1. 用 InsightFace 提取人脸特征向量
    2. 在 Milvus face_vectors 中检索相似人脸
    3. 关联到对应素材
    """
    # TODO: 实现人脸检索逻辑
    return SearchResponse(
        total=0,
        page=page,
        page_size=page_size,
        search_type=SearchType.FACE,
        items=[],
    )
