from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi_jwt_auth import AuthJWT
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from app.db import SessionLocal
from app.models.user import User
from passlib.hash import bcrypt

router = APIRouter()

class UserCreate(BaseModel):
    username: str
    password: str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 注册
@router.post("/api/auth/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter_by(username=user.username).first():
        raise HTTPException(status_code=400, detail="用户已存在")
    db_user = User(username=user.username, hashed_password=bcrypt.hash(user.password))
    db.add(db_user)
    db.commit()
    return {"msg": "注册成功"}

# 登录
@router.post("/api/auth/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), Authorize: AuthJWT = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not bcrypt.verify(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    token = Authorize.create_access_token(subject=user.username)
    return {"access_token": token}
