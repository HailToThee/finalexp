from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

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

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}  # SQLite需要这个参数
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()