from fastapi import APIRouter, UploadFile, File, HTTPException
import os
import shutil
import zipfile
from datetime import datetime

router = APIRouter()
UPLOAD_DIR = "backend/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as f:
        f.write(await file.read())
    return {"filename": file.filename}

@router.get("/list")
def list_files():
    files = os.listdir(UPLOAD_DIR)
    return {"files": files}

@router.get("/info")
def file_info(filename: str):
    file_path = os.path.join(UPLOAD_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="文件不存在")
    stat = os.stat(file_path)
    return {
        "size": stat.st_size,
        "ctime": datetime.fromtimestamp(stat.st_ctime).strftime("%Y-%m-%d %H:%M:%S"),
        "mtime": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
        "type": filename.split('.')[-1]
    }

@router.post("/compress")
def compress_files(filenames: list):
    zip_name = "archive.zip"
    zip_path = os.path.join(UPLOAD_DIR, zip_name)
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for fname in filenames:
            fpath = os.path.join(UPLOAD_DIR, fname)
            if os.path.exists(fpath):
                zipf.write(fpath, arcname=fname)
    return {"zipfile": zip_name}

@router.post("/extract")
def extract_file(zipfile_name: str):
    zip_path = os.path.join(UPLOAD_DIR, zipfile_name)
    if not os.path.exists(zip_path):
        raise HTTPException(status_code=404, detail="压缩包不存在")
    with zipfile.ZipFile(zip_path, 'r') as zipf:
        zipf.extractall(UPLOAD_DIR)
    return {"status": "extracted"}

# routers/images.py
from fastapi import APIRouter, UploadFile, File
router = APIRouter()

@router.post("/api/images/upload")
def upload_image(file: UploadFile = File(...)):
    with open(f"docker_images/{file.filename}", "wb") as f:
        f.write(file.file.read())
    return {"msg": "镜像已保存，待上传 Harbor"}