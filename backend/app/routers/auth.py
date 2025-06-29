from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from pydantic import BaseModel
from typing import Optional
from app.models.user import User
from app.db import get_db
from app.core.security import create_access_token, get_current_user
from datetime import timedelta

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Pydantic models
class UserRegister(BaseModel):
    username: str
    password: str
    nickname: str
    department: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    gender: Optional[str] = None
    position: Optional[str] = None
    remark: Optional[str] = None

class UserLogin(BaseModel):
    username: str
    password: str

@router.post("/register")
async def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """用户注册"""
    try:
        # 检查用户名是否已存在
        existing_user = db.query(User).filter(User.username == user_data.username).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="用户名已存在")
        
        # 检查昵称是否已存在
        existing_nickname = db.query(User).filter(User.nickname == user_data.nickname).first()
        if existing_nickname:
            raise HTTPException(status_code=400, detail="用户昵称已存在")
        
        # 创建新用户
        hashed_password = pwd_context.hash(user_data.password)
        new_user = User(
            username=user_data.username,
            hashed_password=hashed_password,
            nickname=user_data.nickname,
            department=user_data.department,
            phone=user_data.phone,
            email=user_data.email,
            gender=user_data.gender,
            position=user_data.position,
            status="启用",
            remark=user_data.remark
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        return {"msg": "User registered successfully", "user_id": new_user.id}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"注册失败: {str(e)}")

@router.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """用户登录"""
    try:
        user = db.query(User).filter(User.username == form_data.username).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail="用户名或密码错误"
            )
        
        if not pwd_context.verify(form_data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail="用户名或密码错误"
            )
        
        # 检查用户状态
        if user.status != "启用":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, 
                detail="用户已被禁用，请联系管理员"
            )
        
        # 创建访问令牌
        access_token_expires = timedelta(minutes=30)  # 30分钟过期
        access_token = create_access_token(
            data={"sub": user.username}, 
            expires_delta=access_token_expires
        )
        
        return {
            "access_token": access_token, 
            "token_type": "bearer",
            "user_info": {
                "id": user.id,
                "username": user.username,
                "nickname": user.nickname,
                "department": user.department,
                "status": user.status
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"登录失败: {str(e)}")

@router.post("/login")
async def login_json(login_data: UserLogin, db: Session = Depends(get_db)):
    """用户登录（JSON格式）"""
    try:
        user = db.query(User).filter(User.username == login_data.username).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail="用户名或密码错误"
            )
        
        if not pwd_context.verify(login_data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail="用户名或密码错误"
            )
        
        # 检查用户状态
        if user.status != "启用":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, 
                detail="用户已被禁用，请联系管理员"
            )
        
        # 创建访问令牌
        access_token_expires = timedelta(minutes=30)  # 30分钟过期
        access_token = create_access_token(
            data={"sub": user.username}, 
            expires_delta=access_token_expires
        )
        
        return {
            "access_token": access_token, 
            "token_type": "bearer",
            "user_info": {
                "id": user.id,
                "username": user.username,
                "nickname": user.nickname,
                "department": user.department,
                "status": user.status
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"登录失败: {str(e)}")

@router.post("/change-password")
async def change_password(
    old_password: str,
    new_password: str,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """修改密码"""
    try:
        user = db.query(User).filter(User.username == current_user).first()
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")
        
        # 验证旧密码
        if not pwd_context.verify(old_password, user.hashed_password):
            raise HTTPException(status_code=400, detail="原密码错误")
        
        # 更新密码
        user.hashed_password = pwd_context.hash(new_password)
        db.commit()
        
        return {"msg": "密码修改成功"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"密码修改失败: {str(e)}")

@router.get("/profile")
async def get_profile(
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """获取当前用户信息"""
    try:
        user = db.query(User).filter(User.username == current_user).first()
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")
        
        return {
            "id": user.id,
            "username": user.username,
            "nickname": user.nickname,
            "department": user.department,
            "phone": user.phone,
            "email": user.email,
            "gender": user.gender,
            "position": user.position,
            "status": user.status,
            "remark": user.remark,
            "created_at": user.created_at.strftime("%Y-%m-%d %H:%M:%S") if user.created_at else None
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取用户信息失败: {str(e)}")