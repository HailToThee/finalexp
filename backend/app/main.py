from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import auth, file, model, sample, algorithm, attack, evaluation, inference
from app.database.database import engine, Base
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
app.include_router(file.router, prefix="/api/file")
app.include_router(model.router, prefix="/api/model")
app.include_router(sample.router, prefix="/api/sample")
app.include_router(algorithm.router, prefix="/api/algorithm")
app.include_router(attack.router, prefix="/api/attack")
app.include_router(evaluation.router, prefix="/api/evaluation")
app.include_router(inference.router, prefix="/api/inference")
@app.get("/")
async def root():
    return {"message": "Welcome to Model Safety Framework"}