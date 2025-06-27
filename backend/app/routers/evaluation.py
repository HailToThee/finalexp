from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.models.evaluation import Evaluation
from app.database.database import get_db
from datetime import datetime

router = APIRouter()

@router.get("/api/evaluation/list")
def get_evaluations(db: Session = Depends(get_db)):
    evaluations = db.query(Evaluation).all()
    return {"evaluations": [
        {
            "id": e.id,
            "name": e.name,
            "type": e.type,
            "status": e.status,
            "creator": e.creator,
            "result": e.result,#!!!!!!!!!随后需要添加对json的画图功能!!!!!!!!!!!!
            "createdAt": e.created_at.strftime("%Y-%m-%dT%H:%M") if e.created_at else None
        } for e in evaluations
    ]}

@router.post("/api/evaluation/create")
def create_evaluation(evaluation: dict, db: Session = Depends(get_db)):
    if db.query(Evaluation).filter(Evaluation.name == evaluation["name"]).first():
        raise HTTPException(status_code=400, detail="Evaluation existed")
    new_evaluation = Evaluation(
        name=evaluation["name"],
        type=evaluation.get("type"),
        status=evaluation.get("status", "Done"),
        creator=evaluation.get("creator"),
        result=evaluation.get("result"),
        created_at=datetime.strptime(evaluation["createdAt"], "%Y-%m-%dT%H:%M") if evaluation.get("createdAt") else datetime.utcnow()
    )
    db.add(new_evaluation)
    db.commit()
    return {"msg": "Evaluation created"}

@router.delete("/api/evaluation/{id}")
def delete_evaluation(id: int, db: Session = Depends(get_db)):
    evaluation = db.query(Evaluation).filter(Evaluation.id == id).first()
    if not evaluation:
        raise HTTPException(status_code=404, detail="Not exist")
    db.delete(evaluation)
    db.commit()
    return {"msg": "Evaluation deleted"}