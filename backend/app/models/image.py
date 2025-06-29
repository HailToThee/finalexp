from sqlalchemy import Column, Integer, String, DateTime, Text, Float, ForeignKey, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db import Base

class ImageRepository(Base):
    """镜像仓库模型"""
    __tablename__ = "image_repositories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, unique=True)  # 仓库名称
    type = Column(String(100))  # 仓库类型 (x86/arm等)
    description = Column(Text)  # 仓库描述
    creator_id = Column(Integer, nullable=False)  # 创建者ID
    creator_name = Column(String(100), nullable=False)  # 创建者姓名
    is_public = Column(Boolean, default=True)  # 是否公开
    image_count = Column(Integer, default=0)  # 镜像数量
    is_deleted = Column(Integer, default=0)  # 是否删除（软删除）
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 关系
    images = relationship("DockerImage", back_populates="repository")

class DockerImage(Base):
    """Docker镜像模型"""
    __tablename__ = "docker_images"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)  # 镜像名称
    version = Column(String(100), nullable=False)  # 镜像版本
    repo_id = Column(Integer, ForeignKey("image_repositories.id"), nullable=False)  # 所属仓库ID
    file_path = Column(String(500), nullable=False)  # 镜像文件路径
    file_size = Column(Float, nullable=False)  # 文件大小（字节）
    image_size = Column(String(100))  # 镜像大小（如 1.2GB）
    architecture = Column(String(100))  # 架构 (x86_64, arm64等)
    framework = Column(String(100))  # 计算框架 (TensorFlow, PyTorch等)
    description = Column(Text)  # 镜像描述
    usage = Column(String(500))  # 用途说明
    downloads = Column(Integer, default=0)  # 下载次数
    status = Column(String(50), default="ready")  # 状态 (ready, uploading, error)
    permission = Column(String(50), default="public")  # 权限 (public, private)
    creator_id = Column(Integer, nullable=False)  # 创建者ID
    creator_name = Column(String(100), nullable=False)  # 创建者姓名
    is_deleted = Column(Integer, default=0)  # 是否删除（软删除）
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 关系
    repository = relationship("ImageRepository", back_populates="images") 