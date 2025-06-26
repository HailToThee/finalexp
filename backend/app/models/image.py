from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from app.db import Base
from datetime import datetime

class Image(Base):
    __tablename__ = "images"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    tag = Column(String)
    user_id = Column(Integer, ForeignKey("users.id"))
    uploaded_at = Column(DateTime, default=datetime.utcnow)