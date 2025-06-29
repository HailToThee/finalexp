from sqlalchemy import Column, Integer, String, DateTime
from app.db import Base
from datetime import datetime

class InferenceService(Base):
    __tablename__ = "inference_services"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    type = Column(String, nullable=False)
    status = Column(String, default="Running")
    creator = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow) 