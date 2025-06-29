import os
import shutil
import hashlib
import mimetypes
import tarfile
import tempfile
import json
from typing import List, Optional
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Query, Form, Body
from fastapi.responses import FileResponse, JSONResponse
from sqlalchemy.orm import Session
from app.db import get_db
from app.core.security import get_current_user
from app.models.image import DockerImage, ImageRepository
from app.models.user import User
import uuid
from pydantic import BaseModel

router = APIRouter()

# 镜像存储目录
IMAGE_DIR = "uploads/images"
REPO_DIR = os.path.join(IMAGE_DIR, "repositories")

# 确保目录存在
if not os.path.exists(IMAGE_DIR):
    os.makedirs(IMAGE_DIR)
if not os.path.exists(REPO_DIR):
    os.makedirs(REPO_DIR)

def get_image_info(file_path: str) -> dict:
    """获取镜像文件信息"""
    try:
        # 检查文件类型
        if file_path.endswith('.tar') or file_path.endswith('.tar.gz'):
            with tarfile.open(file_path, 'r:*') as tar:
                # 尝试读取镜像信息
                manifest_file = None
                for member in tar.getmembers():
                    if member.name.endswith('manifest.json'):
                        manifest_file = member
                        break
                
                if manifest_file:
                    manifest_content = tar.extractfile(manifest_file).read()
                    # 这里可以解析manifest.json获取更多信息
                    return {
                        "architecture": "x86_64",  # 默认值
                        "framework": "unknown",
                        "image_size": "1.0GB"  # 默认值
                    }
        
        return {
            "architecture": "x86_64",
            "framework": "unknown", 
            "image_size": "1.0GB"
        }
    except Exception as e:
        return {
            "architecture": "x86_64",
            "framework": "unknown",
            "image_size": "1.0GB"
        }

@router.get("/list")
async def get_image_list(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    repo_id: Optional[int] = Query(None),
    keyword: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """获取镜像列表"""
    try:
        query = db.query(DockerImage).filter(DockerImage.is_deleted == 0)
        
        # 按仓库筛选
        if repo_id:
            query = query.filter(DockerImage.repo_id == repo_id)
        
        # 按关键词搜索
        if keyword:
            query = query.filter(DockerImage.name.contains(keyword))
        
        # 分页
        total = query.count()
        images = query.offset((page - 1) * page_size).limit(page_size).all()
        
        image_list = []
        for image in images:
            created_at_str = None
            if image.created_at is not None:
                created_at_str = image.created_at.strftime("%Y-%m-%d %H:%M:%S")
            
            # 获取仓库信息
            repo = db.query(ImageRepository).filter(ImageRepository.id == image.repo_id).first()
            repo_name = repo.name if repo else "未知仓库"
            
            image_list.append({
                "id": image.id,
                "name": image.name,
                "version": image.version,
                "repo_id": image.repo_id,
                "repo_name": repo_name,
                "file_size": image.file_size,
                "image_size": image.image_size,
                "architecture": image.architecture,
                "framework": image.framework,
                "description": image.description,
                "usage": image.usage,
                "downloads": image.downloads,
                "status": image.status,
                "permission": image.permission,
                "creator_name": image.creator_name,
                "createdAt": created_at_str
            })
        
        return {
            "images": image_list,
            "total": total,
            "page": page,
            "page_size": page_size
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取镜像列表失败: {str(e)}")

@router.post("/upload")
async def upload_image(
    file: UploadFile = File(...),
    name: str = Form(...),
    repo_id: int = Form(...),
    version: str = Form(...),
    description: Optional[str] = Form(None),
    usage: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """上传镜像，仓库内不允许同名镜像，版本号可重复"""
    try:
        # 验证仓库是否存在
        repo = db.query(ImageRepository).filter(ImageRepository.id == repo_id).first()
        if not repo:
            raise HTTPException(status_code=404, detail="仓库不存在")
        
        # 检查同仓库同名镜像（不管版本号）
        exist = db.query(DockerImage).filter(DockerImage.repo_id == repo_id, DockerImage.name == name, DockerImage.is_deleted == 0).first()
        if exist:
            raise HTTPException(status_code=400, detail="同一仓库下已存在同名镜像")
        
        # 检查文件类型
        if not file.filename or not file.filename.endswith(('.tar', '.tar.gz', '.img')):
            raise HTTPException(status_code=400, detail="只支持 .tar, .tar.gz, .img 格式的镜像文件")
        
        # 获取用户信息
        user = db.query(User).filter(User.username == current_user).first()
        if not user:
            raise HTTPException(status_code=401, detail="用户不存在或未登录")
        
        # 生成唯一文件名
        file_extension = os.path.splitext(str(file.filename))[1]
        unique_filename = f"{uuid.uuid4().hex}{file_extension}"
        
        # 创建仓库目录
        repo_dir = os.path.join(REPO_DIR, str(repo_id))
        if not os.path.exists(repo_dir):
            os.makedirs(repo_dir)
        
        # 保存文件
        file_path = os.path.join(repo_dir, unique_filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # 获取文件大小
        file_size = os.path.getsize(file_path)
        
        # 获取镜像信息
        image_info = get_image_info(file_path)
        
        # 保存到数据库
        db_image = DockerImage(
            name=name,
            version=version,
            repo_id=repo_id,
            file_path=file_path,
            file_size=file_size,
            image_size=image_info["image_size"],
            architecture=image_info["architecture"],
            framework=image_info["framework"],
            description=description,
            usage=usage,
            creator_id=user.id,
            creator_name=user.nickname if user.nickname else user.username
        )
        db.add(db_image)
        
        # 更新仓库镜像数量
        repo.image_count = (repo.image_count or 0) + 1
        db.commit()
        
        return {"msg": "镜像上传成功", "image_id": db_image.id}
        
    except HTTPException:
        # 重新抛出HTTPException，避免被通用异常处理捕获
        raise
    except Exception as e:
        # 记录详细错误信息用于调试
        print(f"镜像上传异常: {str(e)}")
        raise HTTPException(status_code=500, detail=f"镜像上传失败: {str(e)}")

@router.delete("/{image_id}")
async def delete_image(
    image_id: int,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """删除镜像"""
    try:
        image = db.query(DockerImage).filter(DockerImage.id == image_id, DockerImage.is_deleted == 0).first()
        if not image:
            raise HTTPException(status_code=404, detail="镜像不存在")
        
        # 软删除
        image.is_deleted = 1
        
        # 更新仓库镜像数量
        repo = db.query(ImageRepository).filter(ImageRepository.id == image.repo_id).first()
        if repo and repo.image_count > 0:
            repo.image_count -= 1
        
        db.commit()
        
        return {"msg": "镜像删除成功"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"镜像删除失败: {str(e)}")

@router.get("/detail/{image_id}")
async def get_image_detail(
    image_id: int,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """获取镜像详情"""
    try:
        image = db.query(DockerImage).filter(DockerImage.id == image_id, DockerImage.is_deleted == 0).first()
        if not image:
            raise HTTPException(status_code=404, detail="镜像不存在")
        
        # 获取仓库信息
        repo = db.query(ImageRepository).filter(ImageRepository.id == image.repo_id).first()
        
        created_at_str = None
        if image.created_at is not None:
            created_at_str = image.created_at.strftime("%Y-%m-%d %H:%M:%S")
        
        return {
            "id": image.id,
            "name": image.name,
            "version": image.version,
            "repo_id": image.repo_id,
            "repo_name": repo.name if repo else "未知仓库",
            "file_size": image.file_size,
            "image_size": image.image_size,
            "architecture": image.architecture,
            "framework": image.framework,
            "description": image.description,
            "usage": image.usage,
            "downloads": image.downloads,
            "status": image.status,
            "permission": image.permission,
            "creator_name": image.creator_name,
            "createdAt": created_at_str
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取镜像详情失败: {str(e)}")

@router.get("/download/{image_id}")
async def download_image(
    image_id: int,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """下载镜像文件，仅公开镜像可下载，下载数+1"""
    image = db.query(DockerImage).filter(DockerImage.id == image_id, DockerImage.is_deleted == 0).first()
    if not image:
        raise HTTPException(status_code=404, detail="镜像不存在")
    if image.permission != "public":
        raise HTTPException(status_code=403, detail="该镜像为私有，无法下载")
    if not os.path.exists(image.file_path):
        raise HTTPException(status_code=404, detail="镜像文件不存在")
    # 下载数+1
    image.downloads = (image.downloads or 0) + 1
    db.commit()
    filename = image.name + "-" + image.version + os.path.splitext(image.file_path)[1]
    return FileResponse(image.file_path, filename=filename, media_type="application/octet-stream")

class PushImageRequest(BaseModel):
    id: int

@router.post("/push")
async def push_image(
    request: PushImageRequest,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """推送镜像到远程仓库"""
    try:
        print(f"收到推送请求: image_id={request.id}, user={current_user}")
        
        # 获取镜像信息
        image = db.query(DockerImage).filter(DockerImage.id == request.id, DockerImage.is_deleted == 0).first()
        if not image:
            print(f"镜像不存在: id={request.id}")
            raise HTTPException(status_code=404, detail="镜像不存在")
        
        print(f"找到镜像: {image.name} v{image.version}")
        
        # 检查镜像文件是否存在
        if not os.path.exists(image.file_path):
            print(f"镜像文件不存在: {image.file_path}")
            raise HTTPException(status_code=404, detail="镜像文件不存在")
        
        # 获取用户信息
        user = db.query(User).filter(User.username == current_user).first()
        if not user:
            print(f"用户不存在: {current_user}")
            raise HTTPException(status_code=401, detail="用户不存在或未登录")
        
        print(f"用户验证成功: {user.username}")
        
        # 远程仓库路径
        remote_repo_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "remote_repository", "images")
        print(f"远程仓库路径: {remote_repo_path}")
        
        # 确保远程仓库目录存在
        if not os.path.exists(remote_repo_path):
            os.makedirs(remote_repo_path)
            print(f"创建远程仓库目录: {remote_repo_path}")
        
        # 生成远程文件名（包含时间戳避免冲突）
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        remote_filename = f"{image.name}_{image.version}_{timestamp}{os.path.splitext(image.file_path)[1]}"
        remote_file_path = os.path.join(remote_repo_path, remote_filename)
        print(f"远程文件路径: {remote_file_path}")
        
        # 复制镜像文件到远程仓库
        shutil.copy2(image.file_path, remote_file_path)
        print(f"文件复制成功: {image.file_path} -> {remote_file_path}")
        
        # 更新推送日志
        push_log_path = os.path.join(os.path.dirname(remote_repo_path), "push_log.json")
        push_log = {
            "push_history": [],
            "last_updated": datetime.datetime.now().isoformat()
        }
        
        if os.path.exists(push_log_path):
            try:
                with open(push_log_path, 'r', encoding='utf-8') as f:
                    push_log = json.load(f)
                print(f"读取推送日志: {push_log_path}")
            except Exception as e:
                print(f"读取推送日志失败: {e}")
        
        # 添加推送记录
        push_record = {
            "id": len(push_log["push_history"]) + 1,
            "image_id": image.id,
            "image_name": image.name,
            "image_version": image.version,
            "repo_id": image.repo_id,
            "remote_filename": remote_filename,
            "file_size": image.file_size,
            "pushed_by": user.username,
            "pushed_at": datetime.datetime.now().isoformat(),
            "status": "success"
        }
        
        push_log["push_history"].append(push_record)
        push_log["last_updated"] = datetime.datetime.now().isoformat()
        
        # 保存推送日志
        with open(push_log_path, 'w', encoding='utf-8') as f:
            json.dump(push_log, f, ensure_ascii=False, indent=2)
        print(f"推送日志已保存: {push_log_path}")
        
        # 更新远程仓库统计信息
        config_path = os.path.join(os.path.dirname(remote_repo_path), "config.json")
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                config["statistics"]["total_images"] += 1
                config["statistics"]["push_count"] += 1
                config["statistics"]["last_push"] = datetime.datetime.now().isoformat()
                
                # 计算总大小
                total_size = 0
                for filename in os.listdir(remote_repo_path):
                    file_path = os.path.join(remote_repo_path, filename)
                    if os.path.isfile(file_path):
                        total_size += os.path.getsize(file_path)
                
                # 转换为可读格式
                if total_size < 1024:
                    size_str = f"{total_size}B"
                elif total_size < 1024 * 1024:
                    size_str = f"{total_size / 1024:.1f}KB"
                elif total_size < 1024 * 1024 * 1024:
                    size_str = f"{total_size / (1024 * 1024):.1f}MB"
                else:
                    size_str = f"{total_size / (1024 * 1024 * 1024):.1f}GB"
                
                config["statistics"]["total_size"] = size_str
                
                with open(config_path, 'w', encoding='utf-8') as f:
                    json.dump(config, f, ensure_ascii=False, indent=2)
                print(f"远程仓库配置已更新: {config_path}")
            except Exception as e:
                print(f"更新远程仓库配置失败: {str(e)}")
        
        result = {
            "msg": "镜像推送成功",
            "image_id": image.id,
            "image_name": image.name,
            "image_version": image.version,
            "remote_filename": remote_filename,
            "pushed_at": push_record["pushed_at"],
            "file_size": image.file_size,
            "image_size": image.image_size
        }
        
        print(f"推送成功: {result}")
        return result
        
    except HTTPException:
        print("HTTPException被抛出")
        raise
    except Exception as e:
        print(f"推送镜像异常: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"镜像推送失败: {str(e)}")

@router.get("/repo/list")
async def get_repo_list(
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """获取仓库列表"""
    try:
        repos = db.query(ImageRepository).filter(ImageRepository.is_deleted == 0).all()
        
        repo_list = []
        for repo in repos:
            created_at_str = None
            if repo.created_at is not None:
                created_at_str = repo.created_at.strftime("%Y-%m-%d %H:%M:%S")
            
            repo_list.append({
                "id": repo.id,
                "name": repo.name,
                "type": repo.type,
                "description": repo.description,
                "is_public": repo.is_public,
                "image_count": repo.image_count,
                "creator_name": repo.creator_name,
                "created_at": created_at_str
            })
        
        return {"repos": repo_list}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取仓库列表失败: {str(e)}")

@router.post("/repo/create")
async def create_repo(
    name: str = Form(...),
    type: str = Form(...),
    description: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """创建仓库"""
    try:
        # 检查仓库名称是否已存在
        existing_repo = db.query(ImageRepository).filter(ImageRepository.name == name, ImageRepository.is_deleted == 0).first()
        if existing_repo:
            raise HTTPException(status_code=400, detail="仓库名称已存在")
        
        # 获取用户信息
        user = db.query(User).filter(User.username == current_user).first()
        if not user:
            raise HTTPException(status_code=401, detail="用户不存在或未登录")
        
        # 创建仓库
        repo = ImageRepository(
            name=name,
            type=type,
            description=description,
            creator_id=user.id,
            creator_name=user.nickname if user.nickname else user.username
        )
        
        db.add(repo)
        db.commit()
        
        return {"msg": "仓库创建成功", "repo_id": repo.id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"仓库创建失败: {str(e)}")

@router.post("/permission")
async def update_permission(
    id: int = Form(...),
    permission: str = Form(...),
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """更新镜像权限"""
    try:
        image = db.query(DockerImage).filter(DockerImage.id == id, DockerImage.is_deleted == 0).first()
        if not image:
            raise HTTPException(status_code=404, detail="镜像不存在")
        
        if permission not in ["public", "private"]:
            raise HTTPException(status_code=400, detail="权限值无效")
        
        image.permission = permission
        db.commit()
        
        return {"msg": "权限更新成功"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"权限更新失败: {str(e)}")

@router.get("/push/history")
async def get_push_history(
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """获取推送历史"""
    try:
        # 远程仓库路径
        remote_repo_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "remote_repository", "images")
        push_log_path = os.path.join(os.path.dirname(remote_repo_path), "push_log.json")
        
        if not os.path.exists(push_log_path):
            return {"push_history": [], "total": 0}
        
        with open(push_log_path, 'r', encoding='utf-8') as f:
            push_log = json.load(f)
        
        return {
            "push_history": push_log.get("push_history", []),
            "total": len(push_log.get("push_history", [])),
            "last_updated": push_log.get("last_updated")
        }
        
    except Exception as e:
        print(f"获取推送历史异常: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取推送历史失败: {str(e)}")

@router.get("/push/status")
async def get_push_status(
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """获取远程仓库状态"""
    try:
        # 远程仓库路径
        remote_repo_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "remote_repository", "images")
        config_path = os.path.join(os.path.dirname(remote_repo_path), "config.json")
        
        if not os.path.exists(config_path):
            return {
                "repository": {
                    "name": "FINAL_EXP_Remote_Repository",
                    "status": "not_configured"
                },
                "statistics": {
                    "total_images": 0,
                    "total_size": "0B",
                    "push_count": 0
                }
            }
        
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        return {
            "repository": config.get("repository", {}),
            "statistics": config.get("statistics", {}),
            "settings": config.get("settings", {})
        }
        
    except Exception as e:
        print(f"获取推送状态异常: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取推送状态失败: {str(e)}") 