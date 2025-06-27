from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi_jwt_auth import AuthJWT
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from passlib.hash import bcrypt

from app.db import SessionLocal
from app.models.user import User

router = APIRouter()

# Pydantic模型，用于注册数据验证
class UserCreate(BaseModel):
    username: str
    password: str

# 依赖获取数据库会话
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 注册接口
@router.post("/api/auth/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    # 查询是否已存在用户名
    if db.query(User).filter(User.username == user.username).first():
        raise HTTPException(status_code=400, detail="用户已存在")
    
    # 创建用户
    hashed_pwd = bcrypt.hash(user.password)
    db_user = User(username=user.username, hashed_password=hashed_pwd)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return {"msg": "注册成功", "username": db_user.username, "id": db_user.id}

# 登录接口，返回JWT
@router.post("/api/auth/token")
def token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    Authorize: AuthJWT = Depends(),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not bcrypt.verify(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="用户名或密码错误")

    access_token = Authorize.create_access_token(subject=user.username)
    return {"access_token": access_token, "token_type": "bearer"}

# @router.get("/api/auth/token")
