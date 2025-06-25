from pydantic import BaseSettings

class Settings(BaseSettings):
    SECRET_KEY: str = "your-secret-key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    DATABASE_URL: str = "postgresql://user:password@db:5432/modelsafety"

    class Config:
          env_file = ".env"
          env_file_encoding = "utf-8"

settings = Settings()