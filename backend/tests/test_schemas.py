"""
测试 Pydantic Schemas - 数据校验
"""
from datetime import datetime

import pytest
from pydantic import ValidationError


class TestMaterialSchemas:
    """素材 Schema 测试"""

    def test_material_upload_meta_defaults(self):
        """上传元数据默认值"""
        from app.schemas.material import MaterialUploadMeta
        meta = MaterialUploadMeta()
        assert meta.event_name is None
        assert meta.security_level.value == "internal"
        assert meta.tags == []

    def test_material_upload_meta_with_values(self):
        """上传元数据完整填充"""
        from app.schemas.material import MaterialUploadMeta
        meta = MaterialUploadMeta(
            event_name="2024年表彰大会",
            security_level="public",
            description="活动照片",
            tags=["党建", "表彰"],
        )
        assert meta.event_name == "2024年表彰大会"
        assert len(meta.tags) == 2

    def test_material_update_partial(self):
        """素材更新 - 部分字段"""
        from app.schemas.material import MaterialUpdate
        update = MaterialUpdate(title="新标题")
        data = update.model_dump(exclude_unset=True)
        assert "title" in data
        assert "description" not in data

    def test_material_list_response(self):
        """素材列表响应构造"""
        from app.schemas.material import MaterialListResponse
        resp = MaterialListResponse(total=100, page=1, page_size=20, items=[])
        assert resp.total == 100
        assert resp.items == []

    def test_tag_response(self):
        """标签响应"""
        from app.schemas.material import TagResponse
        tag = TagResponse(id=1, name="党建", category="keyword")
        assert tag.id == 1
        assert tag.name == "党建"


class TestSearchSchemas:
    """检索 Schema 测试"""

    def test_search_request_defaults(self):
        """检索请求默认值"""
        from app.schemas.search import SearchRequest
        req = SearchRequest(query="测试")
        assert req.search_type.value == "text"
        assert req.page == 1
        assert req.page_size == 20
        assert req.exclude_duplicates is True

    def test_search_request_with_filters(self):
        """检索请求带筛选条件"""
        from app.schemas.search import SearchRequest
        req = SearchRequest(
            query="表彰大会",
            material_type="image",
            date_from="2024-01-01",
            date_to="2024-12-31",
            min_quality=60.0,
            page=2,
            page_size=50,
        )
        assert req.material_type == "image"
        assert req.page == 2
        assert req.min_quality == 60.0

    def test_search_request_page_validation(self):
        """页码验证 - 最小值"""
        from app.schemas.search import SearchRequest
        with pytest.raises(ValidationError):
            SearchRequest(query="test", page=0)

    def test_search_request_page_size_max(self):
        """每页数量 - 最大值"""
        from app.schemas.search import SearchRequest
        with pytest.raises(ValidationError):
            SearchRequest(query="test", page_size=200)

    def test_search_response_structure(self):
        """检索响应结构"""
        from app.schemas.search import SearchResponse, SearchType
        resp = SearchResponse(
            total=5, page=1, page_size=20,
            search_type=SearchType.TEXT, query="test", items=[],
        )
        assert resp.total == 5
        assert resp.search_type == SearchType.TEXT

    def test_search_result_item(self):
        """检索结果项"""
        from app.schemas.search import SearchResultItem
        item = SearchResultItem(
            material_id=1, filename="photo.jpg",
            material_type="image", relevance_score=0.95,
            security_level="internal",
        )
        assert item.relevance_score == 0.95
        assert item.timestamp_start is None


class TestUserSchemas:
    """用户 Schema 测试"""

    def test_user_create_validation(self):
        """用户创建 - 字段校验"""
        from app.schemas.user import UserCreate
        user = UserCreate(username="zhangsan", password="123456")
        assert user.username == "zhangsan"
        assert user.role.value == "user"

    def test_user_create_short_username(self):
        """用户名过短"""
        from app.schemas.user import UserCreate
        with pytest.raises(ValidationError):
            UserCreate(username="a", password="123456")

    def test_user_create_short_password(self):
        """密码过短"""
        from app.schemas.user import UserCreate
        with pytest.raises(ValidationError):
            UserCreate(username="zhangsan", password="123")

    def test_user_update_partial(self):
        """用户更新 - 部分字段"""
        from app.schemas.user import UserUpdate
        update = UserUpdate(display_name="张三")
        data = update.model_dump(exclude_unset=True)
        assert data == {"display_name": "张三"}

    def test_login_request(self):
        """登录请求"""
        from app.schemas.user import LoginRequest
        req = LoginRequest(username="admin", password="admin123")
        assert req.username == "admin"

    def test_token_response(self):
        """Token 响应"""
        from app.schemas.user import TokenResponse, UserResponse
        user_resp = UserResponse(
            id=1, username="test", role="user",
            is_active=True, created_at=datetime(2024, 1, 1),
        )
        token = TokenResponse(access_token="xxx.yyy.zzz", user=user_resp)
        assert token.token_type == "bearer"
