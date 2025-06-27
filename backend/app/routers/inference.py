from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.models.inference_service import InferenceService
from app.database.database import get_db
from datetime import datetime

router = APIRouter()

@router.get("/api/inference/list")
def get_services(db: Session = Depends(get_db)):
    services = db.query(InferenceService).all()
    return {"services": [
        {
            "id": s.id,
            "name": s.name,
            "type": s.type,
            "status": s.status,
            "creator": s.creator,
            "createdAt": s.created_at.strftime("%Y-%m-%dT%H:%M") if s.created_at else None
        } for s in services
    ]}

@router.post("/api/inference/deploy")
def create_service(service: dict, db: Session = Depends(get_db)):
    if db.query(InferenceService).filter(InferenceService.name == service["name"]).first():
        raise HTTPException(status_code=400, detail="服务名已存在")
    new_service = InferenceService(
        name=service["name"],
        type=service["type"],
        status=service.get("status", "运行中"),
        creator=service["creator"],
        created_at=datetime.strptime(service["createdAt"], "%Y-%m-%dT%H:%M") if service.get("createdAt") else datetime.utcnow()
    )
    db.add(new_service)
    db.commit()
    return {"msg": "Service created"}

@router.delete("/api/inference/{id}")
def delete_service(id: int, db: Session = Depends(get_db)):
    service = db.query(InferenceService).filter(InferenceService.id == id).first()
    if not service:
        raise HTTPException(status_code=404, detail="服务不存在")
    db.delete(service)
    db.commit()
    return {"msg": "Service deleted"}