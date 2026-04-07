"""
数据库种子数据 - 初始化测试/演示数据
用法: python -m app.seeds.seed_data
"""
import asyncio
import hashlib
import random
from datetime import datetime, timezone, timedelta

from sqlalchemy import select
from loguru import logger

from app.core.database import async_session_factory, init_db
from app.core.security import hash_password
from app.models.user import User, Role, RoleEnum
from app.models.material import (
    Material, MaterialType, MaterialStatus, SecurityLevel,
    Tag, TagCategory, FaceLibrary, material_tag_table,
)
from app.models.audit_log import AuditLog, DownloadRecord, ActionType


# ── 种子数据定义 ─────────────────────────────────────────────────

ROLES = [
    {"name": "super_admin", "display_name": "超级管理员", "description": "系统最高权限"},
    {"name": "manager", "display_name": "素材管理员", "description": "负责素材审核与管理"},
    {"name": "user", "display_name": "普通用户", "description": "素材检索与使用"},
    {"name": "guest", "display_name": "访客", "description": "仅可浏览公开素材"},
]

USERS = [
    {"username": "admin", "password": "admin123", "display_name": "系统管理员",
     "email": "admin@company.com", "department": "信息技术部", "role": RoleEnum.SUPER_ADMIN},
    {"username": "manager01", "password": "manager123", "display_name": "张素材",
     "email": "zhangsc@company.com", "department": "党群工作部", "role": RoleEnum.MANAGER},
    {"username": "manager02", "password": "manager123", "display_name": "李管理",
     "email": "ligl@company.com", "department": "品牌宣传部", "role": RoleEnum.MANAGER},
    {"username": "user01", "password": "user123", "display_name": "王宣传",
     "email": "wangxc@company.com", "department": "品牌宣传部", "role": RoleEnum.USER},
    {"username": "user02", "password": "user123", "display_name": "刘行政",
     "email": "liuxz@company.com", "department": "综合管理部", "role": RoleEnum.USER},
    {"username": "user03", "password": "user123", "display_name": "陈党建",
     "email": "chendj@company.com", "department": "党群工作部", "role": RoleEnum.USER},
    {"username": "user04", "password": "user123", "display_name": "杨设计",
     "email": "yangsj@company.com", "department": "品牌宣传部", "role": RoleEnum.USER},
    {"username": "guest01", "password": "guest123", "display_name": "访客用户",
     "email": "guest@company.com", "department": "外部", "role": RoleEnum.GUEST},
]

TAGS_DATA = {
    TagCategory.PERSON: ["总经理", "副总经理", "党委书记", "纪委书记", "工会主席",
                          "团委书记", "人力资源总监", "财务总监"],
    TagCategory.SCENE: ["会议室", "大礼堂", "户外广场", "办公室", "展厅",
                         "培训室", "食堂", "运动场"],
    TagCategory.EVENT: ["2024年度表彰大会", "2024经营总结会", "主题党日活动",
                         "新春联欢会", "职工运动会", "安全生产月", "廉政教育大会",
                         "青年座谈会", "技能比武大赛", "领导视察调研"],
    TagCategory.KEYWORD: ["高清", "合影", "发言", "颁奖", "鼓掌", "签到",
                           "横幅", "展板", "奖杯", "证书", "红旗"],
}

FACE_LIBRARY = [
    {"person_name": "王建国", "person_title": "总经理", "department": "总经理办公室"},
    {"person_name": "李志强", "person_title": "副总经理", "department": "总经理办公室"},
    {"person_name": "张红梅", "person_title": "党委书记", "department": "党群工作部"},
    {"person_name": "刘明华", "person_title": "纪委书记", "department": "纪检监察部"},
    {"person_name": "陈建华", "person_title": "工会主席", "department": "工会"},
    {"person_name": "杨秀英", "person_title": "人力资源总监", "department": "人力资源部"},
    {"person_name": "赵伟", "person_title": "财务总监", "department": "财务部"},
    {"person_name": "周磊", "person_title": "技术总监", "department": "技术研发部"},
]

MATERIALS_IMAGE = [
    {"filename": "IMG_20240601_表彰大会_开幕式.jpg", "event_name": "2024年度表彰大会",
     "event_date": datetime(2024, 6, 1, 9, 0, tzinfo=timezone.utc),
     "security_level": SecurityLevel.INTERNAL, "quality_score": 92.5,
     "ocr_text": "2024年度表彰大会 先进集体 先进个人", "description": "表彰大会开幕式全景"},
    {"filename": "DSC_总经理致辞_001.jpg", "event_name": "2024年度表彰大会",
     "event_date": datetime(2024, 6, 1, 9, 30, tzinfo=timezone.utc),
     "security_level": SecurityLevel.INTERNAL, "quality_score": 88.3,
     "ocr_text": "感谢大家一年来的辛勤付出", "description": "总经理在台上致辞"},
    {"filename": "IMG_颁奖环节_先进集体.jpg", "event_name": "2024年度表彰大会",
     "event_date": datetime(2024, 6, 1, 10, 0, tzinfo=timezone.utc),
     "security_level": SecurityLevel.PUBLIC, "quality_score": 95.1,
     "ocr_text": "先进集体 颁奖", "description": "先进集体颁奖合影"},
    {"filename": "党建活动_主题党日_01.jpg", "event_name": "2024年主题党日活动",
     "event_date": datetime(2024, 7, 1, 14, 0, tzinfo=timezone.utc),
     "security_level": SecurityLevel.INTERNAL, "quality_score": 85.0,
     "ocr_text": "不忘初心 牢记使命", "description": "主题党日活动现场"},
    {"filename": "党建活动_重温入党誓词.jpg", "event_name": "2024年主题党日活动",
     "event_date": datetime(2024, 7, 1, 14, 30, tzinfo=timezone.utc),
     "security_level": SecurityLevel.INTERNAL, "quality_score": 90.2,
     "ocr_text": "入党誓词 为共产主义事业奋斗终身", "description": "全体党员重温入党誓词"},
    {"filename": "领导视察_生产车间_高清.jpg", "event_name": "2024年领导视察调研",
     "event_date": datetime(2024, 8, 15, 10, 0, tzinfo=timezone.utc),
     "security_level": SecurityLevel.RESTRICTED, "quality_score": 78.5,
     "ocr_text": "安全生产 人人有责", "description": "领导在生产车间视察"},
    {"filename": "经营分析会_数据展示.png", "event_name": "2024经营总结会",
     "event_date": datetime(2024, 12, 20, 9, 0, tzinfo=timezone.utc),
     "security_level": SecurityLevel.CONFIDENTIAL, "quality_score": 82.0,
     "ocr_text": "2024年度经营数据 营收增长15%", "description": "经营分析会数据大屏"},
    {"filename": "新春联欢_节目表演.jpg", "event_name": "2025年新春联欢会",
     "event_date": datetime(2025, 1, 20, 19, 0, tzinfo=timezone.utc),
     "security_level": SecurityLevel.PUBLIC, "quality_score": 91.0,
     "ocr_text": None, "description": "新春联欢会文艺节目表演"},
    {"filename": "运动会_百米决赛.jpg", "event_name": "2024年职工运动会",
     "event_date": datetime(2024, 10, 15, 10, 0, tzinfo=timezone.utc),
     "security_level": SecurityLevel.PUBLIC, "quality_score": 87.6,
     "ocr_text": "职工运动会 百米冲刺", "description": "百米决赛冲刺瞬间"},
    {"filename": "安全生产_培训现场.jpg", "event_name": "2024年安全生产月",
     "event_date": datetime(2024, 6, 15, 14, 0, tzinfo=timezone.utc),
     "security_level": SecurityLevel.INTERNAL, "quality_score": 75.3,
     "ocr_text": "安全第一 预防为主 综合治理", "description": "安全生产培训现场"},
]

MATERIALS_VIDEO = [
    {"filename": "2024表彰大会_完整录像.mp4", "event_name": "2024年度表彰大会",
     "event_date": datetime(2024, 6, 1, 9, 0, tzinfo=timezone.utc),
     "security_level": SecurityLevel.INTERNAL, "duration": 5400.0, "fps": 30.0,
     "quality_score": 88.0,
     "asr_text": "各位领导、各位同事，大家上午好！今天我们隆重召开2024年度表彰大会...",
     "description": "表彰大会全程录像 1.5小时"},
    {"filename": "总经理致辞_片段.mp4", "event_name": "2024年度表彰大会",
     "event_date": datetime(2024, 6, 1, 9, 30, tzinfo=timezone.utc),
     "security_level": SecurityLevel.INTERNAL, "duration": 600.0, "fps": 30.0,
     "quality_score": 90.0,
     "asr_text": "同志们，过去一年我们取得了显著成绩，营收同比增长百分之十五...",
     "description": "总经理致辞精彩片段"},
    {"filename": "党建活动纪录片.mp4", "event_name": "2024年主题党日活动",
     "event_date": datetime(2024, 7, 1, 14, 0, tzinfo=timezone.utc),
     "security_level": SecurityLevel.INTERNAL, "duration": 1800.0, "fps": 25.0,
     "quality_score": 85.5,
     "asr_text": "为庆祝建党纪念日，公司党委组织开展了主题党日活动...",
     "description": "主题党日活动纪录短片"},
    {"filename": "安全教育培训视频.mp4", "event_name": "2024年安全生产月",
     "event_date": datetime(2024, 6, 15, 14, 0, tzinfo=timezone.utc),
     "security_level": SecurityLevel.PUBLIC, "duration": 2400.0, "fps": 30.0,
     "quality_score": 82.0,
     "asr_text": "安全生产是企业发展的基石，今天我们来学习消防安全知识...",
     "description": "消防安全培训教学视频"},
]


# ── 种子数据写入 ─────────────────────────────────────────────────

async def seed_all():
    """写入全部种子数据"""
    await init_db()
    logger.info("🌱 开始写入种子数据...")

    async with async_session_factory() as db:
        try:
            # 1. 角色
            for role_data in ROLES:
                existing = await db.execute(select(Role).where(Role.name == role_data["name"]))
                if not existing.scalar_one_or_none():
                    db.add(Role(**role_data))
            await db.flush()
            logger.info(f"✅ 角色数据: {len(ROLES)} 条")

            # 2. 用户
            user_ids = {}
            for u_data in USERS:
                existing = await db.execute(select(User).where(User.username == u_data["username"]))
                if not existing.scalar_one_or_none():
                    user = User(
                        username=u_data["username"],
                        hashed_password=hash_password(u_data["password"]),
                        display_name=u_data["display_name"],
                        email=u_data["email"],
                        department=u_data["department"],
                        role=u_data["role"],
                    )
                    db.add(user)
                    await db.flush()
                    user_ids[u_data["username"]] = user.id
            logger.info(f"✅ 用户数据: {len(USERS)} 条")

            # 3. 标签
            tag_map = {}
            for category, tag_names in TAGS_DATA.items():
                for name in tag_names:
                    existing = await db.execute(
                        select(Tag).where(Tag.name == name, Tag.category == category)
                    )
                    tag = existing.scalar_one_or_none()
                    if not tag:
                        tag = Tag(name=name, category=category)
                        db.add(tag)
                        await db.flush()
                    tag_map[name] = tag.id
            logger.info(f"✅ 标签数据: {sum(len(v) for v in TAGS_DATA.values())} 条")

            # 4. 人脸库
            for f_data in FACE_LIBRARY:
                existing = await db.execute(
                    select(FaceLibrary).where(FaceLibrary.person_name == f_data["person_name"])
                )
                if not existing.scalar_one_or_none():
                    face = FaceLibrary(
                        person_name=f_data["person_name"],
                        person_title=f_data["person_title"],
                        department=f_data["department"],
                        reference_image_path=f"face_library/{f_data['person_name']}.jpg",
                    )
                    db.add(face)
            await db.flush()
            logger.info(f"✅ 人脸库: {len(FACE_LIBRARY)} 条")

            # 5. 图片素材
            uploader_id = user_ids.get("manager01", 2)
            for m_data in MATERIALS_IMAGE:
                file_hash = hashlib.md5(m_data["filename"].encode()).hexdigest()
                material = Material(
                    filename=m_data["filename"],
                    file_path=f"image/{file_hash[:2]}/{file_hash}/{m_data['filename']}",
                    thumbnail_path=f"thumbnails/{file_hash}_thumb.jpg",
                    file_size=random.randint(1_000_000, 12_000_000),
                    file_hash=file_hash,
                    mime_type="image/jpeg",
                    material_type=MaterialType.IMAGE,
                    width=random.choice([1920, 3840, 4096]),
                    height=random.choice([1080, 2160, 2732]),
                    title=m_data["filename"].rsplit(".", 1)[0],
                    description=m_data["description"],
                    event_name=m_data["event_name"],
                    event_date=m_data["event_date"],
                    status=MaterialStatus.APPROVED,
                    security_level=m_data["security_level"],
                    quality_score=m_data["quality_score"],
                    ocr_text=m_data.get("ocr_text"),
                    uploaded_by=uploader_id,
                    upload_source="seed",
                )
                db.add(material)
            await db.flush()
            logger.info(f"✅ 图片素材: {len(MATERIALS_IMAGE)} 条")

            # 6. 视频素材
            for m_data in MATERIALS_VIDEO:
                file_hash = hashlib.md5(m_data["filename"].encode()).hexdigest()
                material = Material(
                    filename=m_data["filename"],
                    file_path=f"video/{file_hash[:2]}/{file_hash}/{m_data['filename']}",
                    thumbnail_path=f"thumbnails/{file_hash}_thumb.jpg",
                    preview_path=f"previews/{file_hash}_preview.mp4",
                    file_size=random.randint(100_000_000, 2_000_000_000),
                    file_hash=file_hash,
                    mime_type="video/mp4",
                    material_type=MaterialType.VIDEO,
                    width=1920,
                    height=1080,
                    duration=m_data["duration"],
                    fps=m_data["fps"],
                    frame_count=random.randint(10, 50),
                    title=m_data["filename"].rsplit(".", 1)[0],
                    description=m_data["description"],
                    event_name=m_data["event_name"],
                    event_date=m_data["event_date"],
                    status=MaterialStatus.APPROVED,
                    security_level=m_data["security_level"],
                    quality_score=m_data["quality_score"],
                    asr_text=m_data.get("asr_text"),
                    uploaded_by=uploader_id,
                    upload_source="seed",
                )
                db.add(material)
            await db.flush()
            logger.info(f"✅ 视频素材: {len(MATERIALS_VIDEO)} 条")

            # 7. 审计日志样例
            actions = [ActionType.VIEW, ActionType.DOWNLOAD, ActionType.UPLOAD]
            for _ in range(30):
                log = AuditLog(
                    user_id=random.choice(list(user_ids.values())) if user_ids else 1,
                    action=random.choice(actions),
                    resource_type="material",
                    resource_id=random.randint(1, 14),
                    ip_address=f"192.168.1.{random.randint(10, 200)}",
                    user_agent="Mozilla/5.0 Chrome/120.0",
                )
                db.add(log)
            await db.flush()
            logger.info("✅ 审计日志: 30 条")

            await db.commit()
            logger.info("🎉 种子数据写入完成!")

        except Exception as e:
            await db.rollback()
            logger.error(f"❌ 种子数据写入失败: {e}")
            raise


if __name__ == "__main__":
    asyncio.run(seed_all())
