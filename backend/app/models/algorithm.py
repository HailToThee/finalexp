from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from app.db import Base

class Algorithm(Base):
    __tablename__ = "algorithms"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    uploader = Column(String, nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="未部署")
    filepath = Column(String, nullable=False)