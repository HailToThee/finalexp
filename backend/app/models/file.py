from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from app.db import Base

class UploadedFile(Base):
    __tablename__ = "uploaded_files"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)           # 文件名
    path = Column(String, nullable=False)           # 存储路径
    uploader = Column(String, nullable=True)        # 上传者
    uploaded_at = Column(DateTime, default=datetime.utcnow)
