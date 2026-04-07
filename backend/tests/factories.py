"""
测试数据工厂 - 批量生成各类型测试数据
无需外部依赖（Faker），使用内置随机数据生成
"""
import hashlib
import random
import string
from datetime import datetime, timezone, timedelta
from typing import List, Optional
from unittest.mock import MagicMock

import numpy as np


# ── 随机数据生成工具 ─────────────────────────────────────────────

def _rand_str(length: int = 8) -> str:
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=length))


def _rand_cn_name() -> str:
    surnames = ["张", "李", "王", "刘", "陈", "杨", "赵", "黄", "周", "吴"]
    names = ["伟", "芳", "秀英", "敏", "静", "强", "磊", "洋", "勇", "军", "杰", "娜", "涛", "明"]
    return random.choice(surnames) + random.choice(names) + random.choice(names[:5])


def _rand_department() -> str:
    return random.choice([
        "党群工作部", "综合管理部", "人力资源部", "财务部",
        "技术研发部", "市场营销部", "品牌宣传部", "行政后勤部",
    ])


def _rand_event_name() -> str:
    years = ["2023年", "2024年", "2025年"]
    events = [
        "表彰大会", "经营总结会", "党建活动", "领导视察",
        "职工运动会", "新春联欢会", "安全生产月", "技能比武",
        "主题党日活动", "廉政教育大会", "青年座谈会", "工会活动",
    ]
    return random.choice(years) + random.choice(events)


def _rand_file_hash() -> str:
    return hashlib.md5(_rand_str(32).encode()).hexdigest()


def _rand_ip() -> str:
    return f"192.168.{random.randint(1,254)}.{random.randint(1,254)}"


# ── 用户数据工厂 ─────────────────────────────────────────────────

class UserFactory:
    """用户测试数据工厂"""

    _counter = 0

    ROLES = ["super_admin", "manager", "user", "guest"]
    TITLES = ["部门经理", "高级专员", "专员", "实习生", "主任", "副主任"]

    @classmethod
    def create(cls, **overrides) -> MagicMock:
        cls._counter += 1
        user = MagicMock()
        user.id = overrides.get("id", cls._counter)
        user.username = overrides.get("username", f"user_{_rand_str(5)}")
        user.display_name = overrides.get("display_name", _rand_cn_name())
        user.email = overrides.get("email", f"{user.username}@company.com")
        user.department = overrides.get("department", _rand_department())
        user.role = overrides.get("role", "user")
        user.is_active = overrides.get("is_active", True)
        user.hashed_password = overrides.get(
            "hashed_password",
            "$2b$12$" + _rand_str(53)
        )
        user.last_login_at = overrides.get("last_login_at", None)
        user.created_at = overrides.get(
            "created_at",
            datetime(2024, 1, 1, tzinfo=timezone.utc) + timedelta(days=random.randint(0, 365))
        )
        user.updated_at = overrides.get("updated_at", user.created_at)
        user.avatar_url = overrides.get("avatar_url", None)
        user.role_id = overrides.get("role_id", None)
        user.role_rel = overrides.get("role_rel", None)
        return user

    @classmethod
    def create_batch(cls, count: int, **overrides) -> List[MagicMock]:
        return [cls.create(**overrides) for _ in range(count)]

    @classmethod
    def create_admin(cls, **overrides) -> MagicMock:
        defaults = {"role": "super_admin", "username": "admin", "display_name": "系统管理员"}
        defaults.update(overrides)
        return cls.create(**defaults)

    @classmethod
    def create_manager(cls, **overrides) -> MagicMock:
        defaults = {"role": "manager", "username": "manager", "display_name": "素材管理员"}
        defaults.update(overrides)
        return cls.create(**defaults)


# ── 素材数据工厂 ─────────────────────────────────────────────────

class MaterialFactory:
    """素材测试数据工厂"""

    _counter = 0

    IMAGE_FILENAMES = [
        "IMG_20240601_开幕式.jpg", "DSC_表彰现场_001.png",
        "党建活动_合影.jpeg", "领导讲话_高清.jpg",
        "会议室全景.png", "颁奖典礼.webp",
        "参观学习_01.jpg", "座谈会现场.bmp",
    ]

    VIDEO_FILENAMES = [
        "2024表彰大会_完整版.mp4", "领导致辞_片段.mp4",
        "党建活动纪录片.avi", "运动会精彩集锦.mov",
        "新春联欢_节目汇演.mkv", "安全教育_培训视频.mp4",
    ]

    STATUSES = ["pending", "processing", "approved", "rejected", "archived"]
    SECURITY_LEVELS = ["public", "internal", "restricted", "confidential"]

    @classmethod
    def create_image(cls, **overrides) -> MagicMock:
        cls._counter += 1
        m = MagicMock()
        m.id = overrides.get("id", cls._counter)
        m.filename = overrides.get("filename", random.choice(cls.IMAGE_FILENAMES))
        m.file_hash = overrides.get("file_hash", _rand_file_hash())
        m.file_path = overrides.get("file_path", f"image/{m.file_hash[:2]}/{m.file_hash}/{m.filename}")
        m.thumbnail_path = overrides.get("thumbnail_path", f"thumbnails/{m.file_hash}_thumb.jpg")
        m.preview_path = overrides.get("preview_path", None)
        m.file_size = overrides.get("file_size", random.randint(500_000, 15_000_000))
        m.mime_type = overrides.get("mime_type", "image/jpeg")
        m.material_type = "image"
        m.width = overrides.get("width", random.choice([1920, 3840, 4096, 1280]))
        m.height = overrides.get("height", random.choice([1080, 2160, 2160, 720]))
        m.duration = None
        m.fps = None
        m.frame_count = None
        m.title = overrides.get("title", m.filename.rsplit(".", 1)[0])
        m.description = overrides.get("description", f"素材描述-{_rand_str(10)}")
        m.event_name = overrides.get("event_name", _rand_event_name())
        m.event_date = overrides.get(
            "event_date",
            datetime(2024, random.randint(1, 12), random.randint(1, 28), tzinfo=timezone.utc)
        )
        m.status = overrides.get("status", "approved")
        m.security_level = overrides.get("security_level", "internal")
        m.quality_score = overrides.get("quality_score", round(random.uniform(40, 98), 1))
        m.is_duplicate = overrides.get("is_duplicate", False)
        m.duplicate_group_id = overrides.get("duplicate_group_id", None)
        m.ocr_text = overrides.get("ocr_text", random.choice([
            "2024年度表彰大会", "党群工作部", "安全生产月",
            "先进个人", "优秀团队", None, "",
        ]))
        m.asr_text = None
        m.uploaded_by = overrides.get("uploaded_by", random.randint(1, 10))
        m.upload_source = overrides.get("upload_source", "web")
        m.created_at = overrides.get(
            "created_at",
            datetime(2024, 1, 1, tzinfo=timezone.utc) + timedelta(days=random.randint(0, 500))
        )
        m.updated_at = overrides.get("updated_at", m.created_at)
        m.expires_at = overrides.get("expires_at", None)
        m.tags = overrides.get("tags", [])
        m.faces = overrides.get("faces", [])
        m.uploader = overrides.get("uploader", None)
        return m

    @classmethod
    def create_video(cls, **overrides) -> MagicMock:
        cls._counter += 1
        m = MagicMock()
        m.id = overrides.get("id", cls._counter)
        m.filename = overrides.get("filename", random.choice(cls.VIDEO_FILENAMES))
        m.file_hash = overrides.get("file_hash", _rand_file_hash())
        m.file_path = overrides.get("file_path", f"video/{m.file_hash[:2]}/{m.file_hash}/{m.filename}")
        m.thumbnail_path = overrides.get("thumbnail_path", f"thumbnails/{m.file_hash}_thumb.jpg")
        m.preview_path = overrides.get("preview_path", f"previews/{m.file_hash}_preview.mp4")
        m.file_size = overrides.get("file_size", random.randint(50_000_000, 2_000_000_000))
        m.mime_type = overrides.get("mime_type", "video/mp4")
        m.material_type = "video"
        m.width = overrides.get("width", 1920)
        m.height = overrides.get("height", 1080)
        m.duration = overrides.get("duration", round(random.uniform(30, 7200), 2))
        m.fps = overrides.get("fps", random.choice([24.0, 25.0, 30.0, 60.0]))
        m.frame_count = overrides.get("frame_count", random.randint(5, 50))
        m.title = overrides.get("title", m.filename.rsplit(".", 1)[0])
        m.description = overrides.get("description", f"视频描述-{_rand_str(10)}")
        m.event_name = overrides.get("event_name", _rand_event_name())
        m.event_date = overrides.get(
            "event_date",
            datetime(2024, random.randint(1, 12), random.randint(1, 28), tzinfo=timezone.utc)
        )
        m.status = overrides.get("status", "approved")
        m.security_level = overrides.get("security_level", "internal")
        m.quality_score = overrides.get("quality_score", round(random.uniform(50, 95), 1))
        m.is_duplicate = overrides.get("is_duplicate", False)
        m.duplicate_group_id = overrides.get("duplicate_group_id", None)
        m.ocr_text = overrides.get("ocr_text", None)
        m.asr_text = overrides.get("asr_text", random.choice([
            "各位领导、各位同事大家好，今天我们在这里召开年度表彰大会。",
            "下面请获奖代表上台领奖。让我们用热烈的掌声表示祝贺。",
            "感谢各位的辛勤付出，希望新的一年再创佳绩。",
            None,
        ]))
        m.uploaded_by = overrides.get("uploaded_by", random.randint(1, 10))
        m.upload_source = overrides.get("upload_source", "web")
        m.created_at = overrides.get(
            "created_at",
            datetime(2024, 1, 1, tzinfo=timezone.utc) + timedelta(days=random.randint(0, 500))
        )
        m.updated_at = overrides.get("updated_at", m.created_at)
        m.expires_at = overrides.get("expires_at", None)
        m.tags = overrides.get("tags", [])
        m.faces = overrides.get("faces", [])
        m.uploader = overrides.get("uploader", None)
        return m

    @classmethod
    def create_batch_images(cls, count: int, **overrides) -> List[MagicMock]:
        return [cls.create_image(**overrides) for _ in range(count)]

    @classmethod
    def create_batch_videos(cls, count: int, **overrides) -> List[MagicMock]:
        return [cls.create_video(**overrides) for _ in range(count)]

    @classmethod
    def create_duplicate_group(cls, count: int = 3) -> List[MagicMock]:
        """创建一组重复素材"""
        shared_hash = _rand_file_hash()
        group_id = _rand_str(16)
        return [
            cls.create_image(
                file_hash=shared_hash,
                is_duplicate=(i > 0),
                duplicate_group_id=group_id,
                quality_score=round(90 - i * 10, 1),
            )
            for i in range(count)
        ]

    @classmethod
    def create_expired(cls, **overrides) -> MagicMock:
        """创建已过期素材"""
        return cls.create_image(
            expires_at=datetime(2023, 1, 1, tzinfo=timezone.utc),
            status="approved",
            **overrides,
        )


# ── 标签数据工厂 ─────────────────────────────────────────────────

class TagFactory:
    """标签测试数据工厂"""

    _counter = 0

    TAG_DATA = {
        "person": ["总经理", "副总经理", "党委书记", "工会主席", "团委书记"],
        "scene": ["会议室", "大礼堂", "户外", "办公室", "展厅", "食堂"],
        "event": ["表彰大会", "党建活动", "经营分析会", "新春联欢会", "运动会"],
        "keyword": ["高清", "合影", "发言", "颁奖", "鼓掌", "签到", "横幅"],
        "ai_generated": ["室内场景", "多人合影", "舞台", "演讲", "夜景"],
    }

    @classmethod
    def create(cls, **overrides) -> MagicMock:
        cls._counter += 1
        category = overrides.get("category", random.choice(list(cls.TAG_DATA.keys())))
        tag = MagicMock()
        tag.id = overrides.get("id", cls._counter)
        tag.name = overrides.get("name", random.choice(cls.TAG_DATA[category]))
        tag.category = category
        tag.created_at = overrides.get(
            "created_at",
            datetime(2024, 1, 1, tzinfo=timezone.utc)
        )
        tag.materials = overrides.get("materials", [])
        return tag

    @classmethod
    def create_batch(cls, count: int, category: Optional[str] = None) -> List[MagicMock]:
        overrides = {"category": category} if category else {}
        return [cls.create(**overrides) for _ in range(count)]


# ── 人脸数据工厂 ─────────────────────────────────────────────────

class FaceFactory:
    """人脸测试数据工厂"""

    _counter = 0

    @classmethod
    def create_face_library_entry(cls, **overrides) -> MagicMock:
        """创建人脸库条目"""
        cls._counter += 1
        face = MagicMock()
        face.id = overrides.get("id", cls._counter)
        face.person_name = overrides.get("person_name", _rand_cn_name())
        face.person_title = overrides.get("person_title", random.choice([
            "总经理", "副总经理", "部门经理", "高级专员", "党委书记",
        ]))
        face.department = overrides.get("department", _rand_department())
        face.reference_image_path = overrides.get(
            "reference_image_path",
            f"face_library/{face.person_name}_{_rand_str(6)}.jpg"
        )
        face.vector_id = overrides.get("vector_id", _rand_str(16))
        face.is_active = overrides.get("is_active", True)
        face.created_at = overrides.get(
            "created_at",
            datetime(2024, 1, 1, tzinfo=timezone.utc)
        )
        face.appearances = overrides.get("appearances", [])
        return face

    @classmethod
    def create_material_face(cls, **overrides) -> MagicMock:
        """创建素材-人脸关联"""
        cls._counter += 1
        mf = MagicMock()
        mf.id = overrides.get("id", cls._counter)
        mf.material_id = overrides.get("material_id", random.randint(1, 100))
        mf.face_library_id = overrides.get("face_library_id", random.randint(1, 20))
        mf.bbox_x = overrides.get("bbox_x", random.randint(50, 500))
        mf.bbox_y = overrides.get("bbox_y", random.randint(50, 400))
        mf.bbox_w = overrides.get("bbox_w", random.randint(80, 200))
        mf.bbox_h = overrides.get("bbox_h", random.randint(80, 250))
        mf.confidence = overrides.get("confidence", round(random.uniform(0.85, 0.999), 3))
        mf.expression = overrides.get("expression", random.choice([
            "happy", "neutral", "serious", "surprised",
        ]))
        mf.age = overrides.get("age", random.randint(25, 60))
        mf.gender = overrides.get("gender", random.choice(["M", "F"]))
        mf.material = overrides.get("material", None)
        mf.face_person = overrides.get("face_person", None)
        return mf

    @classmethod
    def create_face_embedding(cls, dim: int = 512) -> np.ndarray:
        """生成归一化人脸特征向量"""
        v = np.random.randn(dim).astype(np.float32)
        return v / np.linalg.norm(v)


# ── 审计日志数据工厂 ─────────────────────────────────────────────

class AuditLogFactory:
    """审计日志测试数据工厂"""

    _counter = 0

    ACTIONS = ["view", "download", "upload", "delete", "edit", "approve", "reject", "archive"]
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) Safari/605.1",
        "Mozilla/5.0 (X11; Linux x86_64) Firefox/121.0",
    ]

    @classmethod
    def create(cls, **overrides) -> MagicMock:
        cls._counter += 1
        log = MagicMock()
        log.id = overrides.get("id", cls._counter)
        log.user_id = overrides.get("user_id", random.randint(1, 10))
        log.action = overrides.get("action", random.choice(cls.ACTIONS))
        log.resource_type = overrides.get("resource_type", "material")
        log.resource_id = overrides.get("resource_id", random.randint(1, 500))
        log.detail = overrides.get("detail", None)
        log.ip_address = overrides.get("ip_address", _rand_ip())
        log.user_agent = overrides.get("user_agent", random.choice(cls.USER_AGENTS))
        log.created_at = overrides.get(
            "created_at",
            datetime(2024, 1, 1, tzinfo=timezone.utc) + timedelta(
                days=random.randint(0, 365),
                hours=random.randint(8, 18),
                minutes=random.randint(0, 59),
            )
        )
        log.user = overrides.get("user", UserFactory.create(id=log.user_id))
        return log

    @classmethod
    def create_batch(cls, count: int, **overrides) -> List[MagicMock]:
        return [cls.create(**overrides) for _ in range(count)]


class DownloadRecordFactory:
    """下载记录工厂"""

    _counter = 0

    @classmethod
    def create(cls, **overrides) -> MagicMock:
        cls._counter += 1
        r = MagicMock()
        r.id = overrides.get("id", cls._counter)
        r.user_id = overrides.get("user_id", random.randint(1, 10))
        r.material_id = overrides.get("material_id", random.randint(1, 200))
        r.download_purpose = overrides.get("download_purpose", random.choice([
            "宣传稿制作", "会议材料", "领导汇报", "党建展板", "公众号推文",
        ]))
        r.ip_address = overrides.get("ip_address", _rand_ip())
        r.with_watermark = overrides.get("with_watermark", random.choice(["yes", "no"]))
        r.created_at = overrides.get(
            "created_at",
            datetime(2024, 1, 1, tzinfo=timezone.utc) + timedelta(days=random.randint(0, 365))
        )
        r.user = overrides.get("user", UserFactory.create(id=r.user_id))
        r.material = overrides.get("material", MaterialFactory.create_image(id=r.material_id))
        return r

    @classmethod
    def create_batch(cls, count: int, **overrides) -> List[MagicMock]:
        return [cls.create(**overrides) for _ in range(count)]
