from pydantic import BaseModel
from fastapi_jwt_auth import AuthJWT
from app.config import Settings

class Settings(BaseModel):
    authjwt_secret_key: str = "jwt_hello_world"  # 这串字符串你自己定义，最好复杂一些

@AuthJWT.load_config
def get_config():
    return Settings()