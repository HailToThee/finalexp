from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from app.db import Base

class ModelFile(Base):
    __tablename__ = "model_files"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)        # 模型名或文件名
    type = Column(String, nullable=False)        # "zip" 或 "file"
    path = Column(String, nullable=False)        # 存储路径
    uploader = Column(String, nullable=True)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
