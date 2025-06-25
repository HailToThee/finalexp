from fastapi import APIRouter, Depends
from app.core.security import get_current_user
router = APIRouter()
@router.post("/upload")
async def upload_sample(current_user: str = Depends(get_current_user)):
    return {"msg": "Sample uploaded (placeholder)"}