from fastapi import FastAPI
from app.routers import auth, files, images, org

app = FastAPI()

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(files.router, prefix="/api/files", tags=["files"])
app.include_router(images.router, prefix="/api/images", tags=["images"])
app.include_router(org.router, prefix="/api/org", tags=["org"])
