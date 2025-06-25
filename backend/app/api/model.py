from fastapi import APIRouter, Depends
from app.core.security import get_current_user
router = APIRouter()
@router.post("/upload")
async def upload_model(current_user: str = Depends(get_current_user)):
    return {"msg": "Model uploaded (placeholder)"}