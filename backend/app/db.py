from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

SQLALCHEMY_DATABASE_URL = "postgresql://user:password@db:5432/modelsafety_db"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ✅ main.py 注册模型并连接路由
from fastapi import FastAPI
from app.routers import auth, user, files, images

app = FastAPI()
app.include_router(auth.router)
app.include_router(user.router)
app.include_router(files.router)
app.include_router(images.router)