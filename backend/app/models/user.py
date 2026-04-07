"""
用户与角色模型
"""
import enum
from datetime import datetime, timezone

from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, Enum, ForeignKey, Text,
)
from sqlalchemy.orm import relationship

from app.core.database import Base


class RoleEnum(str, enum.Enum):
    SUPER_ADMIN = "super_admin"       # 超级管理员
    MANAGER = "manager"               # 素材管理员
    USER = "user"                     # 普通用户
    GUEST = "guest"                   # 访客


class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), unique=True, nullable=False, comment="角色标识")
    display_name = Column(String(100), nullable=False, comment="角色显示名称")
    description = Column(Text, comment="角色描述")
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    users = relationship("User", back_populates="role_rel")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False, index=True, comment="用户名")
    hashed_password = Column(String(255), nullable=False, comment="密码哈希")
    display_name = Column(String(100), comment="显示名称")
    email = Column(String(100), comment="邮箱")
    department = Column(String(100), comment="部门")
    role = Column(
        Enum(RoleEnum),
        default=RoleEnum.USER,
        nullable=False,
        comment="角色",
    )
    role_id = Column(Integer, ForeignKey("roles.id"), comment="角色ID")
    is_active = Column(Boolean, default=True, comment="是否启用")
    avatar_url = Column(String(500), comment="头像URL")
    last_login_at = Column(DateTime(timezone=True), comment="最后登录时间")
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    role_rel = relationship("Role", back_populates="users")
