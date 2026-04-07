"""
测试 app.core.security - 认证与安全模块
"""
from datetime import timedelta
from unittest.mock import patch, MagicMock

import pytest
from fastapi import HTTPException


class TestPasswordHashing:
    """密码加密测试"""

    def test_hash_password(self):
        """测试密码哈希"""
        from app.core.security import hash_password
        hashed = hash_password("test123")
        assert hashed != "test123"
        assert hashed.startswith("$2b$")

    def test_verify_password_correct(self):
        """测试正确密码验证"""
        from app.core.security import hash_password, verify_password
        hashed = hash_password("mypassword")
        assert verify_password("mypassword", hashed) is True

    def test_verify_password_wrong(self):
        """测试错误密码验证"""
        from app.core.security import hash_password, verify_password
        hashed = hash_password("mypassword")
        assert verify_password("wrongpassword", hashed) is False

    def test_hash_is_unique(self):
        """每次哈希结果不同（salt不同）"""
        from app.core.security import hash_password
        h1 = hash_password("same")
        h2 = hash_password("same")
        assert h1 != h2


class TestJWT:
    """JWT Token 测试"""

    def test_create_access_token(self):
        """测试创建 token"""
        from app.core.security import create_access_token
        token = create_access_token(data={"sub": "123"})
        assert isinstance(token, str)
        assert len(token) > 20

    def test_decode_access_token_valid(self):
        """测试解码有效 token"""
        from app.core.security import create_access_token, decode_access_token
        token = create_access_token(data={"sub": "42", "role": "admin"})
        payload = decode_access_token(token)
        assert payload["sub"] == "42"
        assert payload["role"] == "admin"
        assert "exp" in payload

    def test_decode_access_token_invalid(self):
        """测试解码无效 token 抛异常"""
        from app.core.security import decode_access_token
        with pytest.raises(HTTPException) as exc_info:
            decode_access_token("invalid.token.here")
        assert exc_info.value.status_code == 401

    def test_token_with_custom_expiry(self):
        """测试自定义过期时间"""
        from app.core.security import create_access_token, decode_access_token
        token = create_access_token(
            data={"sub": "1"},
            expires_delta=timedelta(hours=1),
        )
        payload = decode_access_token(token)
        assert payload["sub"] == "1"

    def test_token_contains_expiry(self):
        """token 中包含 exp 字段"""
        from app.core.security import create_access_token, decode_access_token
        token = create_access_token(data={"sub": "99"})
        payload = decode_access_token(token)
        assert "exp" in payload
