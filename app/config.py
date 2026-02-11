from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Optional
import os

class Settings(BaseSettings):
    ENV: str = "local"
    
    # Database
    SQLALCHEMY_DATABASE_URL: str = "postgresql://user:password@localhost:5432/reverb"
    
    # Auth
    SECRET_KEY: str = "super-secret-key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 1 week
    
    # Gemini
    GEMINI_API_KEY: Optional[str] = None
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000"
    ]

    model_config = SettingsConfigDict(
        env_file=(".env", f".env.{os.getenv('ENV', 'local')}"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
