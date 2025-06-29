from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from app.db import Base

class Sample(Base):
    __tablename__ = "samples"  
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)         
    uploader = Column(String, nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
