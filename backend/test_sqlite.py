#!/usr/bin/env python3
"""
SQLite配置测试脚本
用于验证数据库配置是否正确
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# 添加app目录到Python路径
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app'))

from app.db import Base, SQLALCHEMY_DATABASE_URL

def test_sqlite_connection():
    """测试SQLite连接和基本操作"""
    print("🔍 测试SQLite数据库配置...")
    
    try:
        # 创建引擎
        engine = create_engine(
            SQLALCHEMY_DATABASE_URL,
            connect_args={"check_same_thread": False}
        )
        print("✅ 数据库引擎创建成功")
        
        # 测试连接
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            print("✅ 数据库连接测试成功")
        
        # 测试创建表
        Base.metadata.create_all(bind=engine)
        print("✅ 数据库表创建测试成功")
        
        # 测试会话创建
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        db.close()
        print("✅ 数据库会话测试成功")
        
        print("\n🎉 所有SQLite测试通过！")
        return True
        
    except Exception as e:
        print(f"❌ SQLite测试失败: {e}")
        return False

if __name__ == "__main__":
    test_sqlite_connection() 