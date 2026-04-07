"""
公共依赖注入
"""
from functools import lru_cache
from typing import Optional

import redis.asyncio as aioredis
from elasticsearch import AsyncElasticsearch
from minio import Minio

from app.core.config import get_settings

settings = get_settings()


# ── Redis Client ─────────────────────────────────────────────────
@lru_cache()
def get_redis_client() -> aioredis.Redis:
    return aioredis.from_url(
        settings.REDIS_URL,
        decode_responses=True,
    )


# ── Elasticsearch Client ────────────────────────────────────────
@lru_cache()
def get_es_client() -> AsyncElasticsearch:
    return AsyncElasticsearch(
        hosts=[settings.ES_URL],
        request_timeout=30,
    )


# ── MinIO Client ────────────────────────────────────────────────
@lru_cache()
def get_minio_client() -> Minio:
    return Minio(
        endpoint=settings.MINIO_ENDPOINT,
        access_key=settings.MINIO_ACCESS_KEY,
        secret_key=settings.MINIO_SECRET_KEY,
        secure=settings.MINIO_SECURE,
    )


# ── Milvus Connection ───────────────────────────────────────────
def get_milvus_connection_params() -> dict:
    return {
        "host": settings.MILVUS_HOST,
        "port": settings.MILVUS_PORT,
    }
