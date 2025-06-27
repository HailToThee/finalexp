from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import Session
from datetime import datetime
import os

from app.db import SessionLocal
from app.models.user import User

router = APIRouter()
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/user/list")
def get_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return {"users": [
        {
            "id": u.id,
            "nickname": u.nickname,
            "username": u.username,
            "department": u.department,
            "phone": u.phone,
            "status": u.status,
            "createdAt": u.created_at.strftime("%Y-%m-%dT%H:%M") if u.created_at else None
        } for u in users
    ]}

@router.post("/user/create")
def create_user(user: dict, db: Session = Depends(get_db)):
    if db.query(User).filter(User.username == user["username"]).first():
        raise HTTPException(status_code=400, detail="用户名已存在")
    new_user = User(
        nickname=user.get("nickname"),
        username=user["username"],
        department=user.get("department"),
        phone=user.get("phone"),
        status=user.get("status", "启用"),
        created_at=datetime.strptime(user["createdAt"], "%Y-%m-%dT%H:%M") if user.get("createdAt") else datetime.utcnow(),
        hashed_password=""
    )
    db.add(new_user)
    db.commit()
    return {"msg": "User created"}

@router.put("/user/{id}")
def update_user(id: int, user: dict, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="用户不存在")
    for field in ["nickname", "username", "department", "phone", "status", "createdAt"]:
        if field in user:
            if field == "createdAt":
                setattr(db_user, "created_at", datetime.strptime(user[field], "%Y-%m-%dT%H:%M"))
            else:
                setattr(db_user, field if field != "createdAt" else "created_at", user[field])
    db.commit()
    return {"msg": "User updated"}

@router.delete("/user/{id}")
def delete_user(id: int, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="用户不存在")
    db.delete(db_user)
    db.commit()
    return {"msg": "User deleted"}