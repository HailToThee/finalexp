from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import os
import hashlib
from app.database.database import get_db
from app.core.security import get_current_user
router = APIRouter()
UPLOAD_DIR = "uploads/"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)
@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    chunk_number: int = 0,
    total_chunks: int = 1,
    file_id: str = "",
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    file_path = os.path.join(UPLOAD_DIR, file_id or file.filename)
    mode = "ab" if chunk_number > 0 else "wb"
    try:
        with open(file_path, mode) as f:
            content = await file.read()
            f.write(content)
        if chunk_number + 1 == total_chunks:
            return {"msg": "File uploaded successfully", "file_path": file_path}
        return {"msg": f"Chunk {chunk_number} uploaded"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))