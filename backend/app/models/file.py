from sqlalchemy import Column, Integer, String, DateTime, Text, Float, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db import Base

class Folder(Base):
    __tablename__ = "folders"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    parent_id = Column(Integer, ForeignKey("folders.id"), nullable=True)  # 父文件夹ID
    path = Column(String(500), nullable=False)  # 文件夹路径
    uploader_id = Column(Integer, nullable=False)  # 创建者ID
    uploader_name = Column(String(100), nullable=False)  # 创建者姓名
    description = Column(Text)  # 文件夹描述
    is_deleted = Column(Integer, default=0)  # 是否删除（软删除）
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 关系
    parent = relationship("Folder", remote_side=[id])
    children = relationship("Folder", overlaps="parent")
    files = relationship("File", back_populates="folder")

class File(Base):
    __tablename__ = "files"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Float, nullable=False)  # 文件大小（字节）
    file_type = Column(String(100))  # 文件类型
    mime_type = Column(String(100))  # MIME类型
    folder_id = Column(Integer, ForeignKey("folders.id"), nullable=True)  # 所属文件夹ID
    uploader_id = Column(Integer, nullable=False)  # 上传者ID
    uploader_name = Column(String(100), nullable=False)  # 上传者姓名
    description = Column(Text)  # 文件描述
    tags = Column(String(500))  # 文件标签，逗号分隔
    is_deleted = Column(Integer, default=0)  # 是否删除（软删除）
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 关系
    folder = relationship("Folder", back_populates="files")

class FileChunk(Base):
    __tablename__ = "file_chunks"
    
    id = Column(Integer, primary_key=True, index=True)
    file_id = Column(String(100), nullable=False)  # 临时文件ID
    chunk_index = Column(Integer, nullable=False)  # 分块索引
    total_chunks = Column(Integer, nullable=False)  # 总分块数
    chunk_path = Column(String(500), nullable=False)  # 分块文件路径
    chunk_size = Column(Integer, nullable=False)  # 分块大小
    created_at = Column(DateTime(timezone=True), server_default=func.now()) 