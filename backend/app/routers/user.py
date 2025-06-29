from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional
from passlib.context import CryptContext
from app.models.user import User
from app.db import get_db
from app.core.security import get_current_user
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Pydantic models for request/response
class UserCreate(BaseModel):
    username: str
    password: str
    nickname: str
    department: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    gender: Optional[str] = None
    position: Optional[str] = None
    status: str = "启用"
    remark: Optional[str] = None

class UserUpdate(BaseModel):
    nickname: Optional[str] = None
    department: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    gender: Optional[str] = None
    position: Optional[str] = None
    status: Optional[str] = None
    remark: Optional[str] = None
    password: Optional[str] = None

class UserResponse(BaseModel):
    id: int
    username: str
    nickname: str
    department: Optional[str]
    phone: Optional[str]
    email: Optional[str]
    gender: Optional[str]
    position: Optional[str]
    status: str
    remark: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True

@router.get("/list", response_model=dict)
async def get_users(
    nickname: Optional[str] = Query(None, description="用户昵称"),
    username: Optional[str] = Query(None, description="用户名"),
    phone: Optional[str] = Query(None, description="手机号"),
    status: Optional[str] = Query(None, description="用户状态"),
    department: Optional[str] = Query(None, description="部门"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """获取用户列表，支持分页和筛选"""
    try:
        # 构建查询条件
        query = db.query(User)
        
        if nickname:
            query = query.filter(User.nickname.contains(nickname))
        if username:
            query = query.filter(User.username.contains(username))
        if phone:
            query = query.filter(User.phone.contains(phone))
        if status:
            query = query.filter(User.status == status)
        if department:
            query = query.filter(User.department == department)
        
        # 计算总数
        total = query.count()
        
        # 分页
        offset = (page - 1) * page_size
        users = query.offset(offset).limit(page_size).all()
        
        # 转换为响应格式
        user_list = []
        for user in users:
            user_list.append({
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
                "createdAt": user.created_at.strftime("%Y-%m-%d %H:%M:%S") if user.created_at else None
            })
        
        return {
            "users": user_list,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取用户列表失败: {str(e)}")

@router.post("/create", response_model=dict)
async def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """创建新用户"""
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
            status=user_data.status,
            remark=user_data.remark
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        return {"msg": "User created", "user_id": new_user.id}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"创建用户失败: {str(e)}")

@router.put("/{user_id}", response_model=dict)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """更新用户信息"""
    try:
        # 查找用户
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")
        
        # 更新字段
        update_data = user_data.dict(exclude_unset=True)
        
        # 如果更新密码，需要重新哈希
        if "password" in update_data and update_data["password"]:
            update_data["hashed_password"] = pwd_context.hash(update_data.pop("password"))
        
        # 检查昵称唯一性（如果更新昵称）
        if "nickname" in update_data:
            existing_nickname = db.query(User).filter(
                User.nickname == update_data["nickname"],
                User.id != user_id
            ).first()
            if existing_nickname:
                raise HTTPException(status_code=400, detail="用户昵称已存在")
        
        # 更新用户信息
        for field, value in update_data.items():
            setattr(user, field, value)
        
        db.commit()
        db.refresh(user)
        
        return {"msg": "User updated"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"更新用户失败: {str(e)}")

@router.delete("/{user_id}", response_model=dict)
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """删除用户"""
    try:
        # 查找用户
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")
        
        # 不能删除自己
        current_user_obj = db.query(User).filter(User.username == current_user).first()
        if current_user_obj and current_user_obj.id == user_id:
            raise HTTPException(status_code=400, detail="不能删除当前登录用户")
        
        # 删除用户
        db.delete(user)
        db.commit()
        
        return {"msg": "User deleted"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"删除用户失败: {str(e)}")

@router.get("/{user_id}", response_model=UserResponse)
async def get_user_detail(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """获取用户详情"""
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")
        
        return user
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取用户详情失败: {str(e)}")

@router.post("/{user_id}/status", response_model=dict)
async def toggle_user_status(
    user_id: int,
    status: str,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """切换用户状态（启用/禁用）"""
    try:
        if status not in ["启用", "禁用"]:
            raise HTTPException(status_code=400, detail="状态只能是'启用'或'禁用'")
        
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")
        
        # 不能禁用自己
        current_user_obj = db.query(User).filter(User.username == current_user).first()
        if current_user_obj and current_user_obj.id == user_id and status == "禁用":
            raise HTTPException(status_code=400, detail="不能禁用当前登录用户")
        
        user.status = status
        db.commit()
        
        return {"msg": f"用户状态已更新为{status}"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"更新用户状态失败: {str(e)}")

@router.get("/departments/list", response_model=dict)
async def get_departments(
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """获取所有部门列表"""
    try:
        departments = db.query(User.department).filter(
            User.department.isnot(None),
            User.department != ""
        ).distinct().all()
        
        department_list = [dept[0] for dept in departments if dept[0]]
        
        return {"departments": department_list}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取部门列表失败: {str(e)}") 