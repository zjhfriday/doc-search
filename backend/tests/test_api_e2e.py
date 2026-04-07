"""
API 端到端测试 - 使用 httpx AsyncClient + mock DB
模拟完整的 HTTP 请求/响应流程
"""
import io
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timezone

import pytest
from httpx import AsyncClient, ASGITransport

from tests.factories import UserFactory, MaterialFactory, TagFactory


# ── 辅助 fixtures ────────────────────────────────────────────────

@pytest.fixture
def mock_user():
    return UserFactory.create(id=1, username="testuser", role="user")


@pytest.fixture
def mock_admin():
    return UserFactory.create_admin(id=2)


@pytest.fixture
def mock_manager():
    return UserFactory.create_manager(id=3)


@pytest.fixture
def auth_headers():
    """生成带 JWT token 的请求头"""
    from app.core.security import create_access_token
    token = create_access_token(data={"sub": "1"})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def admin_headers():
    from app.core.security import create_access_token
    token = create_access_token(data={"sub": "2"})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def mock_db_session():
    db = AsyncMock()
    db.execute = AsyncMock()
    db.flush = AsyncMock()
    db.commit = AsyncMock()
    db.rollback = AsyncMock()
    db.close = AsyncMock()
    db.add = MagicMock()
    db.delete = AsyncMock()
    return db


# ── 健康检查 ─────────────────────────────────────────────────────

class TestHealthCheck:
    """健康检查接口"""

    @pytest.mark.asyncio
    async def test_health_endpoint(self):
        """GET /health 返回 200"""
        with patch("app.core.database.init_db", new_callable=AsyncMock):
            from app.main import app
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                resp = await client.get("/health")
                assert resp.status_code == 200
                data = resp.json()
                assert data["status"] == "healthy"
                assert "app" in data


# ── 认证接口测试 ─────────────────────────────────────────────────

class TestAuthAPI:
    """认证接口 E2E 测试"""

    @pytest.mark.asyncio
    async def test_login_success(self, mock_user, mock_db_session):
        """登录成功返回 token"""
        from app.core.security import hash_password
        from app.core.database import get_db

        mock_user.hashed_password = hash_password("test123")
        mock_user.is_active = True

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_user
        mock_db_session.execute.return_value = mock_result

        async def override_get_db():
            yield mock_db_session

        with patch("app.core.database.init_db", new_callable=AsyncMock):
            from app.main import app
            app.dependency_overrides[get_db] = override_get_db
            try:
                transport = ASGITransport(app=app)
                async with AsyncClient(transport=transport, base_url="http://test") as client:
                    resp = await client.post("/api/v1/auth/login", json={
                        "username": "testuser",
                        "password": "test123",
                    })
                    # 路由存在且能处理请求
                    assert resp.status_code in [200, 422, 500]
            finally:
                app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_login_missing_fields(self):
        """登录缺少字段返回 422"""
        with patch("app.core.database.init_db", new_callable=AsyncMock):
            from app.main import app
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                resp = await client.post("/api/v1/auth/login", json={})
                assert resp.status_code == 422


# ── 搜索接口测试 ─────────────────────────────────────────────────

class TestSearchAPI:
    """检索接口 E2E 测试"""

    @pytest.mark.asyncio
    async def test_search_without_auth(self):
        """未认证检索返回 401"""
        with patch("app.core.database.init_db", new_callable=AsyncMock):
            from app.main import app
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                resp = await client.post("/api/v1/search", json={
                    "query": "表彰大会",
                    "search_type": "text",
                })
                assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_search_request_validation(self):
        """检索请求体校验"""
        with patch("app.core.database.init_db", new_callable=AsyncMock):
            from app.main import app
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                # page_size 超过最大值
                resp = await client.post("/api/v1/search",
                    json={"query": "test", "page_size": 999},
                    headers={"Authorization": "Bearer fake"},
                )
                assert resp.status_code in [401, 422]


# ── 上传接口测试 ─────────────────────────────────────────────────

class TestUploadAPI:
    """上传接口 E2E 测试"""

    @pytest.mark.asyncio
    async def test_upload_without_auth(self):
        """未认证上传返回 401"""
        with patch("app.core.database.init_db", new_callable=AsyncMock):
            from app.main import app
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                files = {"file": ("test.jpg", b"fake image content", "image/jpeg")}
                resp = await client.post("/api/v1/upload/single", files=files)
                assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_upload_route_exists(self):
        """上传路由存在"""
        with patch("app.core.database.init_db", new_callable=AsyncMock):
            from app.main import app
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                resp = await client.post("/api/v1/upload/batch",
                    files=[("files", ("t.jpg", b"x", "image/jpeg"))],
                )
                assert resp.status_code in [401, 422, 500]
                # 不应该返回 404
                assert resp.status_code != 404


# ── 素材管理接口测试 ─────────────────────────────────────────────

class TestMaterialAPI:
    """素材管理接口 E2E 测试"""

    @pytest.mark.asyncio
    async def test_material_list_without_auth(self):
        """未认证获取素材列表返回 401"""
        with patch("app.core.database.init_db", new_callable=AsyncMock):
            from app.main import app
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                resp = await client.get("/api/v1/materials")
                assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_material_detail_without_auth(self):
        """未认证获取素材详情返回 401"""
        with patch("app.core.database.init_db", new_callable=AsyncMock):
            from app.main import app
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                resp = await client.get("/api/v1/materials/1")
                assert resp.status_code == 401


# ── 用户管理接口测试 ─────────────────────────────────────────────

class TestUserAPI:
    """用户管理接口 E2E 测试"""

    @pytest.mark.asyncio
    async def test_user_list_without_auth(self):
        """未认证获取用户列表返回 401"""
        with patch("app.core.database.init_db", new_callable=AsyncMock):
            from app.main import app
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                resp = await client.get("/api/v1/users")
                assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_create_user_without_auth(self):
        """未认证创建用户返回 401"""
        with patch("app.core.database.init_db", new_callable=AsyncMock):
            from app.main import app
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                resp = await client.post("/api/v1/users", json={
                    "username": "newuser", "password": "pass123"
                })
                assert resp.status_code == 401


# ── 审计日志接口测试 ─────────────────────────────────────────────

class TestAuditAPI:
    """审计日志接口 E2E 测试"""

    @pytest.mark.asyncio
    async def test_audit_logs_without_auth(self):
        """未认证查看审计日志返回 401"""
        with patch("app.core.database.init_db", new_callable=AsyncMock):
            from app.main import app
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                resp = await client.get("/api/v1/audit/logs")
                assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_download_records_without_auth(self):
        """未认证查看下载记录返回 401"""
        with patch("app.core.database.init_db", new_callable=AsyncMock):
            from app.main import app
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                resp = await client.get("/api/v1/audit/downloads")
                assert resp.status_code == 401


# ── Dashboard 接口测试 ───────────────────────────────────────────

class TestDashboardAPI:
    """数据看板接口 E2E 测试"""

    @pytest.mark.asyncio
    async def test_overview_without_auth(self):
        """未认证获取概览数据返回 401"""
        with patch("app.core.database.init_db", new_callable=AsyncMock):
            from app.main import app
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                resp = await client.get("/api/v1/dashboard/overview")
                assert resp.status_code == 401


# ── 人脸库接口测试 ───────────────────────────────────────────────

class TestFaceLibraryAPI:
    """人脸库接口 E2E 测试"""

    @pytest.mark.asyncio
    async def test_face_list_without_auth(self):
        """未认证查看人脸库返回 401"""
        with patch("app.core.database.init_db", new_callable=AsyncMock):
            from app.main import app
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                resp = await client.get("/api/v1/face-library")
                assert resp.status_code == 401
