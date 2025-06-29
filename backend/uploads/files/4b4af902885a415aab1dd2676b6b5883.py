import os
import shutil
import hashlib
import mimetypes
import zipfile
import tarfile
import rarfile
import tempfile
from typing import List, Optional
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Query, Form
from fastapi.responses import FileResponse, JSONResponse
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.core.security import get_current_user
from app.models.file import File as FileModel, FileChunk, Folder
from app.models.user import User
import uuid

router = APIRouter()

# 文件存储目录 - 使用相对路径
UPLOAD_DIR = "uploads"
CHUNK_DIR = os.path.join(UPLOAD_DIR, "chunks")

# 确保目录存在
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)
if not os.path.exists(CHUNK_DIR):
    os.makedirs(CHUNK_DIR)

def get_file_type(filename: str) -> str:
    """获取文件类型"""
    ext = os.path.splitext(filename)[1].lower()
    type_mapping = {
        '.jpg': 'image', '.jpeg': 'image', '.png': 'image', '.gif': 'image', '.bmp': 'image',
        '.mp4': 'video', '.avi': 'video', '.mov': 'video', '.wmv': 'video',
        '.mp3': 'audio', '.wav': 'audio', '.flac': 'audio',
        '.txt': 'text', '.doc': 'document', '.docx': 'document', '.pdf': 'document',
        '.py': 'code', '.js': 'code', '.java': 'code', '.cpp': 'code', '.c': 'code',
        '.zip': 'archive', '.rar': 'archive', '.tar': 'archive', '.gz': 'archive', '.7z': 'archive',
        '.pkl': 'model', '.pth': 'model', '.onnx': 'model', '.h5': 'model'
    }
    return type_mapping.get(ext, 'other')

def create_folder_path(folder_id: int, db: Session) -> str:
    """创建文件夹的物理路径"""
    folder = db.query(Folder).filter(Folder.id == folder_id).first()
    if not folder:
        return UPLOAD_DIR
    
    # 构建文件夹路径
    path_parts = []
    current_folder = folder
    while current_folder:
        path_parts.insert(0, current_folder.name)
        current_folder = current_folder.parent
    
    folder_path = os.path.join(UPLOAD_DIR, *path_parts)
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    
    return folder_path

def add_extracted_files_to_db(extract_dir: str, extracted_files: List[str], db: Session, user: User, original_file_id: int, target_folder_id: Optional[int] = None):
    """将解压后的文件添加到数据库"""
    added_files = []
    
    # 获取目标文件夹路径
    if target_folder_id:
        target_folder_path = create_folder_path(target_folder_id, db)
    else:
        target_folder_path = UPLOAD_DIR
    
    for file_path in extracted_files:
        # 跳过目录
        if file_path.endswith('/') or file_path.endswith('\\'):
            continue
            
        # 构建完整路径
        full_path = os.path.join(extract_dir, file_path)
        
        # 检查文件是否存在
        if not os.path.isfile(full_path):
            continue
            
        # 获取文件信息
        file_size = os.path.getsize(full_path)
        mime_type = mimetypes.guess_type(file_path)[0] if file_path else "application/octet-stream"
        file_type = get_file_type(file_path) if file_path else "other"
        
        # 生成唯一文件名
        file_extension = os.path.splitext(file_path)[1] if file_path else ""
        unique_filename = f"{uuid.uuid4().hex}{file_extension}"
        new_file_path = os.path.join(target_folder_path, unique_filename)
        
        # 移动文件到目标目录
        shutil.move(full_path, new_file_path)
        
        # 保存到数据库
        db_file = FileModel(
            filename=unique_filename,
            original_filename=os.path.basename(file_path) if file_path else "unknown",
            file_path=new_file_path,
            file_size=file_size,
            file_type=file_type,
            mime_type=mime_type,
            folder_id=target_folder_id,
            uploader_id=user.id,
            uploader_name=user.nickname or user.username,
            description=f"从压缩文件解压得到 (原文件ID: {original_file_id})",
            tags="extracted"
        )
        
        db.add(db_file)
        added_files.append({
            "filename": os.path.basename(file_path) if file_path else "unknown",
            "size": file_size,
            "type": file_type
        })
    
    db.commit()
    return added_files

def decompress_archive(file_path: str, extract_dir: str) -> List[str]:
    """解压压缩文件，返回解压出的文件列表"""
    extracted_files = []
    file_ext = os.path.splitext(file_path)[1].lower()
    
    try:
        if file_ext == '.zip':
            with zipfile.ZipFile(file_path, 'r') as zipf:
                zipf.extractall(extract_dir)
                extracted_files = zipf.namelist()
        
        elif file_ext == '.tar' or file_path.endswith('.tar.gz') or file_path.endswith('.tgz'):
            with tarfile.open(file_path, 'r:*') as tarf:
                tarf.extractall(extract_dir)
                extracted_files = tarf.getnames()
        
        elif file_ext == '.rar':
            try:
                with rarfile.RarFile(file_path, 'r') as rarf:
                    rarf.extractall(extract_dir)
                    extracted_files = rarf.namelist()
            except ImportError:
                raise HTTPException(status_code=400, detail="需要安装rarfile库来支持RAR格式")
        
        else:
            raise HTTPException(status_code=400, detail=f"不支持的压缩格式: {file_ext}")
        
        return extracted_files
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"解压失败: {str(e)}")

@router.get("/list")
async def get_file_list(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    file_type: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """获取文件列表"""
    try:
        query = db.query(FileModel).filter(FileModel.is_deleted == 0)
        
        # 按文件类型筛选
        if file_type:
            query = query.filter(FileModel.file_type == file_type)
        
        # 按文件名搜索
        if search:
            query = query.filter(FileModel.original_filename.contains(search))
        
        # 分页
        total = query.count()
        files = query.offset((page - 1) * page_size).limit(page_size).all()
        
        file_list = []
        for file in files:
            created_at_str = None
            if file.created_at is not None:
                created_at_str = file.created_at.strftime("%Y-%m-%d %H:%M:%S")
            
            file_list.append({
                "id": file.id,
                "filename": file.filename,
                "original_filename": file.original_filename,
                "file_size": file.file_size,
                "file_type": file.file_type,
                "mime_type": file.mime_type,
                "uploader_name": file.uploader_name,
                "description": file.description,
                "tags": file.tags,
                "created_at": created_at_str,
                "folder_id": file.folder_id
            })
        
        return {
            "files": file_list,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取文件列表失败: {str(e)}")

@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    description: Optional[str] = Form(None),
    tags: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """上传单个文件"""
    try:
        # 获取用户信息
        user = db.query(User).filter(User.username == current_user).first()
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")
        
        # 确保文件名不为空
        if not file.filename:
            raise HTTPException(status_code=400, detail="文件名不能为空")
        
        # 生成唯一文件名
        file_extension = os.path.splitext(file.filename)[1]
        unique_filename = f"{uuid.uuid4().hex}{file_extension}"
        file_path = os.path.join(UPLOAD_DIR, unique_filename)
        
        # 保存文件
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # 获取文件信息
        file_size = os.path.getsize(file_path)
        mime_type = file.content_type or mimetypes.guess_type(file.filename)[0] or "application/octet-stream"
        file_type = get_file_type(file.filename)
        
        # 文件默认放在默认文件夹下（folder_id为null表示默认文件夹）
        folder_id = None
        
        # 保存到数据库
        db_file = FileModel(
            filename=unique_filename,
            original_filename=file.filename,
            file_path=file_path,
            file_size=file_size,
            file_type=file_type,
            mime_type=mime_type,
            folder_id=folder_id,  # 默认文件夹
            uploader_id=user.id,
            uploader_name=user.nickname or user.username,
            description=description,
            tags=tags
        )
        
        db.add(db_file)
        db.commit()
        
        return {
            "message": "文件上传成功",
            "file_id": db_file.id,
            "filename": file.filename,
            "file_size": file_size,
            "file_type": file_type
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文件上传失败: {str(e)}")

@router.post("/upload_folder")
async def upload_folder(
    files: List[UploadFile] = File(...),
    folder_name: str = Form(...),
    description: Optional[str] = Form(None),
    tags: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """上传文件夹（多个文件）"""
    try:
        # 获取用户信息
        user = db.query(User).filter(User.username == current_user).first()
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")
        
        uploaded_files = []
        
        for file in files:
            # 确保文件名不为空
            if not file.filename:
                continue
                
            # 生成唯一文件名
            file_extension = os.path.splitext(file.filename)[1]
            unique_filename = f"{uuid.uuid4().hex}{file_extension}"
            file_path = os.path.join(UPLOAD_DIR, unique_filename)
            
            # 保存文件
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            # 获取文件信息
            file_size = os.path.getsize(file_path)
            mime_type = file.content_type or mimetypes.guess_type(file.filename)[0] or "application/octet-stream"
            file_type = get_file_type(file.filename)
            
            # 保存到数据库
            db_file = FileModel(
                filename=unique_filename,
                original_filename=file.filename,
                file_path=file_path,
                file_size=file_size,
                file_type=file_type,
                mime_type=mime_type,
                uploader_id=user.id,
                uploader_name=user.nickname or user.username,
                description=f"{description or ''} (文件夹: {folder_name})",
                tags=f"{tags or ''},folder:{folder_name}".strip(',')
            )
            
            db.add(db_file)
            uploaded_files.append({
                "filename": file.filename,
                "size": file_size,
                "type": file_type
            })
        
        db.commit()
        
        return {
            "msg": f"Folder '{folder_name}' uploaded successfully", 
            "uploaded_files": uploaded_files,
            "total_files": len(uploaded_files)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文件夹上传失败: {str(e)}")

@router.post("/upload_chunk")
async def upload_chunk(
    file: UploadFile = File(...),
    name: str = Form(...),
    chunk_index: int = Form(...),
    total_chunks: int = Form(...),
    file_id: str = Form(...),
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """断点续传 - 上传文件分块"""
    try:
        # 创建分块目录
        chunk_dir = os.path.join(CHUNK_DIR, file_id)
        if not os.path.exists(chunk_dir):
            os.makedirs(chunk_dir)
        
        # 保存分块文件
        chunk_path = os.path.join(chunk_dir, f"chunk_{chunk_index}")
        with open(chunk_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # 记录分块信息
        chunk_size = os.path.getsize(chunk_path)
        db_chunk = FileChunk(
            file_id=file_id,
            chunk_index=chunk_index,
            total_chunks=total_chunks,
            chunk_path=chunk_path,
            chunk_size=chunk_size
        )
        
        db.add(db_chunk)
        db.commit()
        
        # 检查是否所有分块都已上传
        uploaded_chunks = db.query(FileChunk).filter(
            FileChunk.file_id == file_id
        ).count()
        
        if uploaded_chunks == total_chunks:
            # 合并所有分块
            final_path = os.path.join(UPLOAD_DIR, f"{file_id}_{name}")
            with open(final_path, "wb") as outfile:
                for i in range(total_chunks):
                    chunk_path = os.path.join(chunk_dir, f"chunk_{i}")
                    with open(chunk_path, "rb") as infile:
                        shutil.copyfileobj(infile, outfile)
            
            # 清理分块文件
            shutil.rmtree(chunk_dir)
            
            # 保存到数据库
            user = db.query(User).filter(User.username == current_user).first()
            if not user:
                raise HTTPException(status_code=404, detail="用户不存在")
                
            file_size = os.path.getsize(final_path)
            mime_type = mimetypes.guess_type(name)[0] or "application/octet-stream"
            file_type = get_file_type(name)
            
            db_file = FileModel(
                filename=f"{file_id}_{name}",
                original_filename=name,
                file_path=final_path,
                file_size=file_size,
                file_type=file_type,
                mime_type=mime_type,
                folder_id=None,  # 默认文件夹
                uploader_id=user.id,
                uploader_name=user.nickname or user.username
            )
            
            db.add(db_file)
            db.commit()
            
            return {"msg": "File uploaded successfully", "file_id": db_file.id}
        
        return {"msg": f"Chunk {chunk_index} uploaded", "uploaded_chunks": uploaded_chunks}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"分块上传失败: {str(e)}")

@router.delete("/{file_id}")
async def delete_file(
    file_id: int,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """删除文件（软删除）"""
    try:
        file = db.query(FileModel).filter(FileModel.id == file_id, FileModel.is_deleted == int(0)).first()
        if not file:
            raise HTTPException(status_code=404, detail="文件不存在")
        
        # 软删除
        file.is_deleted = int(1)
        db.commit()
        
        return {"msg": "File deleted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文件删除失败: {str(e)}")

@router.get("/download/{file_id}")
async def download_file(
    file_id: int,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """下载文件"""
    try:
        file = db.query(FileModel).filter(FileModel.id == file_id, FileModel.is_deleted == int(0)).first()
        if not file:
            raise HTTPException(status_code=404, detail="文件不存在")
        
        file_path_str = str(file.file_path)
        if not os.path.exists(file_path_str):
            raise HTTPException(status_code=404, detail="文件不存在")
        
        media_type = None
        if file.mime_type is not None:
            media_type = str(file.mime_type)
        
        return FileResponse(
            path=file_path_str,
            filename=str(file.original_filename),
            media_type=media_type
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文件下载失败: {str(e)}")

@router.post("/batch_delete")
async def batch_delete_files(
    file_ids: List[int],
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """批量删除文件"""
    try:
        files = db.query(FileModel).filter(FileModel.id.in_(file_ids)).all()
        for file in files:
            file.is_deleted = int(1)
        
        db.commit()
        return {"msg": f"{len(files)} files deleted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"批量删除失败: {str(e)}")

@router.post("/batch_delete_mixed")
async def batch_delete_mixed(
    file_ids: List[int] = Form([]),
    folder_ids: List[int] = Form([]),
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """批量删除文件和文件夹"""
    try:
        deleted_files = 0
        deleted_folders = 0
        
        # 删除文件
        if file_ids:
            files = db.query(FileModel).filter(FileModel.id.in_(file_ids)).all()
            for file in files:
                file.is_deleted = int(1)
            deleted_files = len(files)
        
        # 删除文件夹
        if folder_ids:
            folders = db.query(Folder).filter(Folder.id.in_(folder_ids)).all()
            for folder in folders:
                # 软删除文件夹
                folder.is_deleted = int(1)
                
                # 同时软删除文件夹下的所有文件
                folder_files = db.query(FileModel).filter(FileModel.folder_id == folder.id).all()
                for file in folder_files:
                    file.is_deleted = int(1)
                
                deleted_folders += 1
        
        db.commit()
        
        return {
            "msg": f"批量删除完成",
            "deleted_files": deleted_files,
            "deleted_folders": deleted_folders
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"批量删除失败: {str(e)}")

@router.post("/batch_download")
async def batch_download_files(
    file_ids: List[int],
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """批量下载文件（打包为zip）"""
    try:
        files = db.query(FileModel).filter(
            FileModel.id.in_(file_ids), 
            FileModel.is_deleted == 0
        ).all()
        
        if not files:
            raise HTTPException(status_code=404, detail="没有找到文件")
        
        # 创建临时zip文件
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.zip')
        with zipfile.ZipFile(temp_file.name, 'w') as zipf:
            for file in files:
                file_path_str = str(file.file_path)
                if os.path.exists(file_path_str):
                    zipf.write(file_path_str, str(file.original_filename))
        
        return FileResponse(
            path=temp_file.name,
            filename="batch_download.zip",
            media_type="application/zip"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"批量下载失败: {str(e)}")

@router.post("/batch_download_mixed")
async def batch_download_mixed(
    file_ids: List[int] = Form([]),
    folder_ids: List[int] = Form([]),
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """批量下载文件和文件夹（打包为zip）"""
    try:
        all_files = []
        
        # 获取选中的文件
        if file_ids:
            files = db.query(FileModel).filter(
                FileModel.id.in_(file_ids), 
                FileModel.is_deleted == 0
            ).all()
            all_files.extend(files)
        
        # 获取文件夹中的文件
        if folder_ids:
            for folder_id in folder_ids:
                folder = db.query(Folder).filter(Folder.id == folder_id, Folder.is_deleted == 0).first()
                if folder:
                    # 获取文件夹下的所有文件
                    folder_files = db.query(FileModel).filter(
                        FileModel.folder_id == folder_id,
                        FileModel.is_deleted == 0
                    ).all()
                    
                    all_files.extend(folder_files)
        
        if not all_files:
            raise HTTPException(status_code=404, detail="没有找到文件")
        
        # 创建临时zip文件
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.zip')
        with zipfile.ZipFile(temp_file.name, 'w') as zipf:
            for file in all_files:
                file_path_str = str(file.file_path)
                if os.path.exists(file_path_str):
                    # 确定zip中的文件名
                    zip_filename = str(file.original_filename)
                    
                    # 如果是文件夹中的文件，添加文件夹前缀
                    if file.folder_id and folder_ids:
                        folder = db.query(Folder).filter(Folder.id == file.folder_id).first()
                        if folder:
                            zip_filename = f"{folder.name}/{zip_filename}"
                    
                    zipf.write(file_path_str, zip_filename)
        
        return FileResponse(
            path=temp_file.name,
            filename="batch_download_mixed.zip",
            media_type="application/zip"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"批量下载失败: {str(e)}")

@router.post("/batch_decompress")
async def batch_decompress_files(
    file_ids: List[int],
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """批量解压文件"""
    try:
        files = db.query(FileModel).filter(
            FileModel.id.in_(file_ids), 
            FileModel.is_deleted == 0
        ).all()
        
        if not files:
            raise HTTPException(status_code=404, detail="没有找到文件")
        
        results = []
        for file in files:
            try:
                file_path_str = str(file.file_path)
                if not os.path.exists(file_path_str):
                    results.append({"file_id": file.id, "filename": file.original_filename, "status": "error", "message": "文件不存在"})
                    continue
                
                # 检查是否为压缩文件
                if file.file_type != 'archive':
                    results.append({"file_id": file.id, "filename": file.original_filename, "status": "error", "message": "不是压缩文件"})
                    continue
                
                # 创建解压目录
                extract_dir = os.path.join(UPLOAD_DIR, f"extracted_{file.id}")
                if not os.path.exists(extract_dir):
                    os.makedirs(extract_dir)
                
                # 解压文件
                extracted_files = decompress_archive(file_path_str, extract_dir)
                
                # 将解压后的文件添加到数据库
                user = db.query(User).filter(User.username == current_user).first()
                added_files = add_extracted_files_to_db(extract_dir, extracted_files, db, user, int(file.id))
                
                results.append({
                    "file_id": file.id, 
                    "filename": file.original_filename, 
                    "status": "success", 
                    "extract_dir": extract_dir,
                    "extracted_files": added_files
                })
                
            except Exception as e:
                results.append({"file_id": file.id, "filename": file.original_filename, "status": "error", "message": str(e)})
        
        return {
            "msg": f"批量解压完成，共处理 {len(files)} 个文件",
            "results": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"批量解压失败: {str(e)}")

@router.post("/decompress/{file_id}")
async def decompress_file(
    file_id: int,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """解压单个文件"""
    try:
        file = db.query(FileModel).filter(FileModel.id == file_id, FileModel.is_deleted == int(0)).first()
        if not file:
            raise HTTPException(status_code=404, detail="文件不存在")
        
        file_path_str = str(file.file_path)
        if not os.path.exists(file_path_str):
            raise HTTPException(status_code=404, detail="文件不存在")
        
        # 检查是否为压缩文件
        if file.file_type != 'archive':
            raise HTTPException(status_code=400, detail="不是压缩文件")
        
        # 创建解压目录
        extract_dir = os.path.join(UPLOAD_DIR, f"extracted_{file_id}")
        if not os.path.exists(extract_dir):
            os.makedirs(extract_dir)
        
        # 解压文件
        extracted_files = decompress_archive(file_path_str, extract_dir)
        
        # 将解压后的文件添加到数据库
        user = db.query(User).filter(User.username == current_user).first()
        added_files = add_extracted_files_to_db(extract_dir, extracted_files, db, user, int(file.id))
        
        return {"msg": "File decompressed successfully", "extract_dir": extract_dir, "extracted_files": added_files}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文件解压失败: {str(e)}")

@router.get("/folders")
async def get_folders(
    parent_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """获取文件夹列表"""
    try:
        query = db.query(Folder).filter(Folder.is_deleted == 0)
        
        # 根据新的文件夹结构，所有文件夹都是兄弟关系
        # 如果指定了parent_id，则获取该文件夹下的子文件夹
        # 否则获取所有根级文件夹（parent_id为null的文件夹）
        if parent_id is not None:
            query = query.filter(Folder.parent_id == parent_id)
        else:
            # 获取所有文件夹，都是兄弟关系
            query = query.filter(Folder.parent_id.is_(None))
        
        folders = query.all()
        
        folder_list = []
        for folder in folders:
            created_at_str = None
            if folder.created_at is not None:
                created_at_str = folder.created_at.strftime("%Y-%m-%d %H:%M:%S")
                
            folder_list.append({
                "id": folder.id,
                "name": folder.name,
                "path": folder.path,
                "parent_id": folder.parent_id,
                "uploader_name": folder.uploader_name,
                "description": folder.description,
                "created_at": created_at_str
            })
        
        return {"folders": folder_list}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取文件夹列表失败: {str(e)}")

@router.post("/folders")
async def create_folder(
    name: str = Form(...),
    parent_id: Optional[int] = Form(None),
    description: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """创建文件夹"""
    try:
        # 获取用户信息
        user = db.query(User).filter(User.username == current_user).first()
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")
        
        # 检查文件夹名是否已存在
        existing_folder = db.query(Folder).filter(
            Folder.name == name,
            Folder.parent_id == parent_id,
            Folder.is_deleted == 0
        ).first()
        
        if existing_folder:
            raise HTTPException(status_code=400, detail="文件夹名已存在")
        
        # 构建文件夹路径
        path_parts = [name]
        if parent_id:
            parent_folder = db.query(Folder).filter(Folder.id == parent_id).first()
            if parent_folder:
                path_parts.insert(0, str(parent_folder.path))
        
        folder_path = os.path.join(*path_parts)
        
        # 创建文件夹
        db_folder = Folder(
            name=name,
            parent_id=parent_id,
            path=folder_path,
            uploader_id=user.id,
            uploader_name=user.nickname or user.username,
            description=description
        )
        
        db.add(db_folder)
        db.commit()
        
        # 创建物理文件夹
        physical_path = create_folder_path(int(db_folder.id), db)
        
        return {
            "msg": "Folder created successfully",
            "folder_id": db_folder.id,
            "path": physical_path
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建文件夹失败: {str(e)}")

@router.put("/move/{file_id}")
async def move_file(
    file_id: int,
    folder_id: Optional[int] = Form(None),
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """移动文件到指定文件夹"""
    try:
        # 类型修正，确保folder_id为int
        if folder_id is not None:
            folder_id = int(folder_id)
        file = db.query(FileModel).filter(FileModel.id == file_id, FileModel.is_deleted == int(0)).first()
        if not file:
            raise HTTPException(status_code=404, detail="文件不存在")
        # 如果指定了文件夹，检查文件夹是否存在
        if folder_id:
            folder = db.query(Folder).filter(Folder.id == folder_id, Folder.is_deleted == int(0)).first()
            if not folder:
                raise HTTPException(status_code=404, detail="目标文件夹不存在")
        # 更新文件的文件夹ID
        file.folder_id = folder_id
        db.commit()
        db.refresh(file)
        return {"msg": "File moved successfully", "file": {
            "id": file.id,
            "filename": file.filename,
            "original_filename": file.original_filename,
            "file_path": file.file_path,
            "file_size": file.file_size,
            "file_type": file.file_type,
            "mime_type": file.mime_type,
            "folder_id": file.folder_id,
            "uploader_id": file.uploader_id,
            "uploader_name": file.uploader_name,
            "description": file.description,
            "tags": file.tags,
            "is_deleted": file.is_deleted,
            "created_at": str(file.created_at) if file.created_at else None,
            "updated_at": str(file.updated_at) if file.updated_at else None
        }}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"移动文件失败: {str(e)}")

@router.get("/tree")
async def get_file_tree(
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """获取文件和文件夹树形结构"""
    try:
        def build_tree(parent_id=None):
            # 获取文件夹
            folders = db.query(Folder).filter(
                Folder.parent_id == parent_id,
                Folder.is_deleted == 0
            ).all()
            
            tree = []
            
            for folder in folders:
                folder_node = {
                    "id": folder.id,
                        "name": folder.name,
                        "type": "folder",
                        "path": folder.path,
                        "children": build_tree(folder.id)
                }
                tree.append(folder_node)
            
            # 获取文件
            files = db.query(FileModel).filter(
                FileModel.folder_id == parent_id,
                FileModel.is_deleted == 0
            ).all()
            
            for file in files:
                file_node = {
                    "id": file.id,
                        "name": file.original_filename,
                        "type": "file",
                        "file_type": file.file_type,
                    "size": file.file_size
                }
                tree.append(file_node)
            
            return tree
        
        tree = build_tree()
        return {"tree": tree}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取文件树失败: {str(e)}")

@router.put("/{file_id}/rename")
async def rename_file(
    file_id: int,
    new_name: str = Form(...),
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """重命名文件"""
    try:
        file = db.query(FileModel).filter(FileModel.id == file_id, FileModel.is_deleted == int(0)).first()
        if not file:
            raise HTTPException(status_code=404, detail="文件不存在")
        
        # 检查新文件名是否已存在
        existing_file = db.query(FileModel).filter(
            FileModel.original_filename == new_name,
            FileModel.is_deleted == int(0),
            FileModel.id != file_id
        ).first()
        if existing_file:
            raise HTTPException(status_code=400, detail="文件名已存在")
        
        # 获取文件扩展名
        old_extension = os.path.splitext(str(file.original_filename))[1]
        new_extension = os.path.splitext(new_name)[1]
        
        # 如果新文件名没有扩展名，使用原文件的扩展名
        if not new_extension:
            new_name = new_name + old_extension
        
        # 更新数据库中的文件名
        file.original_filename = new_name
        
        # 更新文件类型
        file.file_type = get_file_type(new_name)
        file.mime_type = mimetypes.guess_type(new_name)[0] or "application/octet-stream"
        
        db.commit()
        
        return {"msg": "File renamed successfully", "new_name": new_name}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"重命名失败: {str(e)}")

@router.delete("/folders/{folder_id}")
async def delete_folder(
    folder_id: int,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """删除文件夹（软删除）"""
    try:
        folder = db.query(Folder).filter(Folder.id == folder_id).first()
        if not folder:
            raise HTTPException(status_code=404, detail="文件夹不存在")
        
        # 软删除文件夹
        folder.is_deleted = int(1)
        
        # 同时软删除文件夹下的所有文件
        files = db.query(FileModel).filter(FileModel.folder_id == folder_id).all()
        for file in files:
            file.is_deleted = int(1)
        
        db.commit()
        
        return {"msg": "Folder deleted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文件夹删除失败: {str(e)}")

@router.put("/folders/{folder_id}/rename")
async def rename_folder(
    folder_id: int,
    new_name: str = Form(...),
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """重命名文件夹"""
    try:
        folder = db.query(Folder).filter(Folder.id == folder_id, Folder.is_deleted == 0).first()
        if not folder:
            raise HTTPException(status_code=404, detail="文件夹不存在")
        
        # 检查新名称是否已存在
        existing_folder = db.query(Folder).filter(
            Folder.name == new_name,
            Folder.parent_id == folder.parent_id,
            Folder.is_deleted == 0,
            Folder.id != folder_id
        ).first()
        if existing_folder:
            raise HTTPException(status_code=400, detail="文件夹名已存在")
        
        # 更新文件夹名称
        folder.name = new_name
        
        # 更新文件夹路径
        path_parts = [new_name]
        if folder.parent_id:
            parent_folder = db.query(Folder).filter(Folder.id == folder.parent_id).first()
            if parent_folder:
                path_parts.insert(0, str(parent_folder.path))
        
        folder.path = os.path.join(*path_parts)
        
        db.commit()
        
        return {"msg": "Folder renamed successfully", "new_name": new_name}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"重命名失败: {str(e)}")