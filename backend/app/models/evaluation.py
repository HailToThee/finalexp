from sqlalchemy import Column, Integer, String, DateTime, JSON
from datetime import datetime
from app.db import Base

class Evaluation(Base):
    __tablename__ = "evaluation"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    type = Column(String)
    status = Column(String, default="Done")
    creator = Column(String)
    result = Column(JSON, default={})  # 存储多个曲线数据
    created_at = Column(DateTime, default=datetime.utcnow)
