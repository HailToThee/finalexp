from fastapi import APIRouter, Depends
from app.core.security import get_current_user
router = APIRouter()
@router.get("/report")
async def get_evaluation_report(current_user: str = Depends(get_current_user)):
    return {"msg": "Evaluation report generated (placeholder)"}