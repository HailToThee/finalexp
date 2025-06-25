from fastapi import APIRouter, Depends
from app.core.security import get_current_user
router = APIRouter()
@router.post("/create")
async def create_attack(current_user: str = Depends(get_current_user)):
    return {"msg": "Attack task created (placeholder)"}