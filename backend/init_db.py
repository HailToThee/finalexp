#!/usr/bin/env python3
"""
数据库初始化脚本
用于创建默认管理员用户和基础数据
"""

import sys
import os
import time
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError
from app.db import Base
from app.models.user import User
from app.models.file import File, FileChunk, Folder
from app.models.algorithm import Algorithm
from app.models.inference_service import InferenceService
from app.models.model_file import ModelFile
from app.models.sample import Sample

from passlib.context import CryptContext

# 将当前脚本的目录添加到 Python 路径，以便导入同级或相对路径模块
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app'))

# 创建密码上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 检测是否在Docker容器中运行
if os.path.exists('/.dockerenv'):
    # Docker容器环境
    DATABASE_FILE = "/app/data/modelsafety.db"
else:
    # 本地开发环境
    DATABASE_FILE = "./data/modelsafety.db"

SQLALCHEMY_DATABASE_URL = f"sqlite:///{DATABASE_FILE}"

# 确保数据目录存在
os.makedirs(os.path.dirname(DATABASE_FILE), exist_ok=True)

# 数据库连接重试配置
MAX_RETRIES = 5
RETRY_DELAY = 2

def init_db_with_retries():
    """
    尝试连接数据库并初始化。
    包含重试机制，以等待数据库服务完全启动。
    """
    engine = None
    for i in range(MAX_RETRIES):
        try:
            print(f"尝试连接数据库... (尝试 {i + 1}/{MAX_RETRIES})")
            engine = create_engine(
                SQLALCHEMY_DATABASE_URL,
                connect_args={"check_same_thread": False}
            )
            # 尝试建立一次连接，以验证数据库是否可用
            with engine.connect() as connection:
                print("成功连接到数据库。")
            break
        except OperationalError as e:
            print(f"数据库连接失败: {e}")
            if i < MAX_RETRIES - 1:
                print(f"将在 {RETRY_DELAY} 秒后重试...")
                time.sleep(RETRY_DELAY)
            else:
                print("已达到最大重试次数。无法连接到数据库。")
                sys.exit(1)

    if engine is None:
        print("未能初始化数据库引擎，脚本退出。")
        sys.exit(1)

    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    print("正在删除所有现有数据库表 (如果存在)...")
    try:
        Base.metadata.drop_all(bind=engine)
        print("所有现有表已删除。")
    except Exception as e:
        print(f"删除表时发生错误 (可能因为表不存在): {e}")

    print("正在检查并创建数据库表 (如果不存在)...")
    try:
        Base.metadata.create_all(bind=engine)
        print("数据库表已成功创建/检查。")
    except Exception as e:
        print(f"创建表时发生错误: {e}")
        sys.exit(1)

    # 创建会话
    db = SessionLocal()

    try:
        # 检查是否已有用户，防止重复创建
        existing_user = db.query(User).first()
        if not existing_user:
            print("正在创建默认用户...")
            # 创建默认管理员用户
            admin_user = User(
                username="admin",
                nickname="管理员",
                email="admin@example.com",
                hashed_password=pwd_context.hash("admin123"),
                department="技术部",
                position="系统管理员"
            )
            db.add(admin_user)
            
            # 创建默认用户
            default_user = User(
                username="user",
                nickname="普通用户",
                email="user@example.com",
                hashed_password=pwd_context.hash("user123"),
                department="用户部",
                position="普通用户"
            )
            db.add(default_user)
            
            # 提交更改
            db.commit()
            print("✅ 数据库初始化完成！")
            print("默认用户:")
            print("  管理员: admin / admin123")
            print("  普通用户: user / user123")
        else:
            print("✅ 数据库已存在用户，跳过默认用户创建。")
    except Exception as e:
        db.rollback()
        print(f"创建用户时发生错误: {e}")
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    init_db_with_retries()