from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, file, user
from app.routers import image  # 新增镜像管理API
from app.db import engine, Base
from app.models import user as user_model, file as file_model  # 导入模型以确保表创建

app = FastAPI(title="Model Safety Framework")
# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Create database tables
Base.metadata.create_all(bind=engine)
# Include API routers
app.include_router(auth.router, prefix="/api/auth")
app.include_router(user.router, prefix="/api/user")
app.include_router(file.router, prefix="/api/file")
app.include_router(image.router, prefix="/api/image")  # 注册镜像管理API

@app.get("/")
async def root():
    return {"message": "Welcome to Model Safety Framework"}