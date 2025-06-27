from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Body
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from fastapi_jwt_auth import AuthJWT

import os, zipfile
from datetime import datetime

from app.db import SessionLocal
from app.models.uploaded_file import UploadedFile

router = APIRouter()
UPLOAD_DIR = "backend/uploads/files"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def is_safe_filename(filename: str) -> bool:
    return os.path.basename(filename) == filename and ".." not in filename

# 上传文件 + 记录数据库
@router.post("/api/file/upload")
async def upload_file(
    file: UploadFile = File(...),
    Authorize: AuthJWT = Depends(),
    db: Session = Depends(get_db)
):
    Authorize.jwt_required()
    username = Authorize.get_jwt_subject()

    filename = os.path.basename(file.filename)
    if not is_safe_filename(filename):
        raise HTTPException(status_code=400, detail="非法文件名")

    file_path = os.path.join(UPLOAD_DIR, filename)
    with open(file_path, "wb") as f:
        f.write(await file.read())

    record = UploadedFile(name=filename, path=file_path, uploader=username)
    db.add(record)
    db.commit()
    db.refresh(record)

    return {"filename": record.name, "id": record.id}

# 文件列表（数据库）
@router.get("/api/file/list")
def list_files(db: Session = Depends(get_db)):
    files = db.query(UploadedFile).all()
    return {
        "files": [
            {
                "id": f.id,
                "name": f.name,
                "uploader": f.uploader,
                "uploadedAt": f.uploaded_at.isoformat()
            }
            for f in files
        ]
    }

# 删除文件
@router.delete("/api/file/{id}")
def delete_file(id: int, db: Session = Depends(get_db)):
    file = db.query(UploadedFile).filter_by(id=id).first()
    if not file:
        raise HTTPException(status_code=404, detail="文件记录不存在")

    if os.path.exists(file.path):
        os.remove(file.path)

    db.delete(file)
    db.commit()
    return {"detail": f"文件 {file.name} 删除成功"}

# 下载文件
@router.get("/api/file/download/{id}")
def download_file(id: int, db: Session = Depends(get_db)):
    file = db.query(UploadedFile).filter_by(id=id).first()
    if not file or not os.path.exists(file.path):
        raise HTTPException(status_code=404, detail="文件不存在")

    return FileResponse(
        path=file.path,
        filename=file.name,
        media_type="application/octet-stream"
    )

# 压缩文件列表为 zip
@router.post("/api/file/compress")
def compress_files(filenames: list[str] = Body(...)):
    zip_name = f"archive_{datetime.now().strftime('%Y%m%d%H%M%S')}.zip"
    zip_path = os.path.join(UPLOAD_DIR, zip_name)

    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for fname in filenames:
            if not is_safe_filename(fname):
                continue
            fpath = os.path.join(UPLOAD_DIR, fname)
            if os.path.exists(fpath):
                zipf.write(fpath, arcname=fname)

    return {"zipfile": zip_name}

# 解压缩 zip 文件
@router.post("/api/file/extract")
def extract_file(zipfile_name: str = Body(...)):
    if not is_safe_filename(zipfile_name):
        raise HTTPException(status_code=400, detail="非法文件名")

    zip_path = os.path.join(UPLOAD_DIR, zipfile_name)
    if not os.path.exists(zip_path):
        raise HTTPException(status_code=404, detail="压缩包不存在")

    try:
        with zipfile.ZipFile(zip_path, 'r') as zipf:
            zipf.extractall(UPLOAD_DIR)
        return {"status": "解压成功"}
    except zipfile.BadZipFile:
        raise HTTPException(status_code=400, detail="无效的 zip 文件")
