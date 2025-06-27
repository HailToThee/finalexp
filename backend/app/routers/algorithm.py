from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
from datetime import datetime
import os
import shutil
import zipfile

from app.db import SessionLocal
from app.models.algorithm import Algorithm

# FastAPI 路由和逻辑
router = APIRouter()
UPLOAD_DIR = "/backend/uploads/algorithm"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def is_safe_name(name: str) -> bool:
    return os.path.basename(name) == name and ".." not in name

@router.get("/api/algorithm/list")
def get_list(db: Session = Depends(get_db)):
    algorithms = db.query(Algorithm).all()
    return {
        "algorithms": [
            {
                "id": alg.id,
                "name": alg.name,
                "uploader": alg.uploader,
                "uploadedAt": alg.uploaded_at.strftime("%Y-%m-%dT%H:%M"),
                "status": alg.status,
            }
            for alg in algorithms
        ]
    }

@router.post("/api/algorithm/upload")
async def upload_algor(algor: UploadFile = File(...), uploader: str = "默认用户", db: Session = Depends(get_db)):
    filename = algor.filename
    base_name, ext = os.path.splitext(filename)

    if not is_safe_name(filename):
        raise HTTPException(status_code=400, detail="Invalid filename")

    if ext not in [".zip", ".py"]:
        raise HTTPException(status_code=400, detail="Only .zip and .py files are allowed")

    existing = db.query(Algorithm).filter(Algorithm.name == base_name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Algorithm with this name already exists")

    try:
        if ext == ".zip":
            folder_path = os.path.join(UPLOAD_DIR, base_name)
            temp_zip_path = folder_path + ".zip"

            with open(temp_zip_path, "wb") as f:
                f.write(await algor.read())

            os.makedirs(folder_path, exist_ok=True)
            with zipfile.ZipFile(temp_zip_path, "r") as zip_ref:
                zip_ref.extractall(folder_path)

            os.remove(temp_zip_path)
            filepath = folder_path
        else:  # .py 文件直接保存
            file_path = os.path.join(UPLOAD_DIR, filename)
            with open(file_path, "wb") as f:
                f.write(await algor.read())
            filepath = file_path

        new_alg = Algorithm(
            name=base_name,
            uploader=uploader,
            uploaded_at=datetime.utcnow(),
            status="未部署",
            filepath=filepath,
        )
        db.add(new_alg)
        db.commit()
        db.refresh(new_alg)

        return {"message": f"Algorithm '{base_name}' uploaded successfully", "id": new_alg.id}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@router.delete("/api/algorithm/{id}")
def delete_algor(id: int, db: Session = Depends(get_db)):
    alg = db.query(Algorithm).filter(Algorithm.id == id).first()
    if not alg:
        raise HTTPException(status_code=404, detail="Algorithm not found")

    try:
        if os.path.isdir(alg.filepath):
            shutil.rmtree(alg.filepath)
        elif os.path.isfile(alg.filepath):
            os.remove(alg.filepath)

        db.delete(alg)
        db.commit()
        return {"message": f"Algorithm '{alg.name}' deleted successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Delete failed: {str(e)}")
