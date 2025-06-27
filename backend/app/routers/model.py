from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
import os, shutil, zipfile
from datetime import datetime
from sqlalchemy.orm import Session
from fastapi_jwt_auth import AuthJWT

from app.db import SessionLocal
from app.models.model_file import ModelFile

router = APIRouter()
UPLOAD_DIR = "backend/uploads/models"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def is_safe_name(name: str) -> bool:
    return os.path.basename(name) == name and ".." not in name

# 获取模型列表（数据库）
@router.get("/api/model/list")
def get_list(db: Session = Depends(get_db)):
    models = db.query(ModelFile).all()
    return {
        "models": [
            {
                "id": m.id,
                "name": m.name,
                "type": m.type,
                "uploader": m.uploader,
                "uploadedAt": m.uploaded_at.isoformat()
            }
            for m in models
        ]
    }

# 上传模型（支持 zip 或普通模型文件）
@router.post("/api/model/upload")
async def upload_model(
    model: UploadFile = File(...),
    Authorize: AuthJWT = Depends(),
    db: Session = Depends(get_db)
):
    Authorize.jwt_required()
    username = Authorize.get_jwt_subject()

    filename = model.filename
    base_name, ext = os.path.splitext(filename)

    if not is_safe_name(filename):
        raise HTTPException(status_code=400, detail="Invalid filename")

    try:
        if ext == ".zip":
            # ZIP 模型上传
            model_dir = os.path.join(UPLOAD_DIR, base_name)
            temp_zip_path = model_dir + ".zip"

            with open(temp_zip_path, "wb") as f:
                f.write(await model.read())

            os.makedirs(model_dir, exist_ok=True)
            with zipfile.ZipFile(temp_zip_path, 'r') as zip_ref:
                zip_ref.extractall(model_dir)

            os.remove(temp_zip_path)

            db_model = ModelFile(
                name=base_name,
                type="zip",
                path=model_dir,
                uploader=username
            )
        else:
            # 普通模型文件上传
            model_path = os.path.join(UPLOAD_DIR, filename)
            with open(model_path, "wb") as f:
                f.write(await model.read())

            db_model = ModelFile(
                name=filename,
                type="file",
                path=model_path,
                uploader=username
            )

        db.add(db_model)
        db.commit()
        db.refresh(db_model)

        return {"message": "Model uploaded", "id": db_model.id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

# 删除模型
@router.delete("/api/model/{id}")
def delete_model(id: int, db: Session = Depends(get_db)):
    model = db.query(ModelFile).filter_by(id=id).first()
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")

    try:
        if os.path.exists(model.path):
            if model.type == "zip":
                shutil.rmtree(model.path)
            else:
                os.remove(model.path)

        db.delete(model)
        db.commit()
        return {"message": f"Model '{model.name}' deleted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Delete failed: {str(e)}")
