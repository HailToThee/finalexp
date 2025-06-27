from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
import os
from datetime import datetime
from sqlalchemy.orm import Session
from fastapi_jwt_auth import AuthJWT

from app.db import SessionLocal
from app.models.sample import Sample

router = APIRouter()
UPLOAD_DIR = "backend/uploads/samples"
os.makedirs(UPLOAD_DIR, exist_ok=True)


# 数据库依赖
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# 5.1 获取样本列表
@router.get("/api/sample/list")
def list_samples(db: Session = Depends(get_db)):
    samples = db.query(Sample).all()
    return {
        "samples": [
            {
                "id": s.id,
                "name": s.name,
                "type": s.type,
                "uploader": s.uploader,
                "uploadedAt": s.uploaded_at.isoformat(timespec="minutes")
            }
            for s in samples
        ]
    }


# 5.2 上传样本
@router.post("/api/sample/upload")
async def upload_sample(
    file: UploadFile = File(...),
    Authorize: AuthJWT = Depends(),
    db: Session = Depends(get_db)
):
    Authorize.jwt_required()
    current_user = Authorize.get_jwt_subject()

    file_path = os.path.join(UPLOAD_DIR, file.filename)
    try:
        with open(file_path, "wb") as f:
            f.write(await file.read())

        sample = Sample(
            name=file.filename,
            type="文本" if file.filename.endswith(".txt") else "未知",
            uploader=current_user,
            uploaded_at=datetime.utcnow()
        )
        db.add(sample)
        db.commit()

        return {"msg": "Sample uploaded successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


# 5.3 删除样本
@router.delete("/api/sample/{id}")
def delete_sample(id: int, db: Session = Depends(get_db)):
    sample = db.query(Sample).filter(Sample.id == id).first()
    if not sample:
        raise HTTPException(status_code=404, detail="Sample not found")

    file_path = os.path.join(UPLOAD_DIR, sample.name)
    try:
        if os.path.exists(file_path):
            os.remove(file_path)

        db.delete(sample)
        db.commit()
        return {"msg": "Sample deleted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Delete failed: {str(e)}")
