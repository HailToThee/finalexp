from fastapi import FastAPI
from app.routers import auth, files, images, org
import app.config 
app = FastAPI()
################main中的库还没有导入####################
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(files.router, prefix="/api/files", tags=["files"])
app.include_router(images.router, prefix="/api/models", tags=["images"])
app.include_router(org.router, prefix="/api/", tags=["org"])
