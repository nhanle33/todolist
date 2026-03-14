from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings from .env file"""
    # App config
    APP_NAME: str = "To-Do List API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # API config
    API_PREFIX: str = "/api/v1"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Global settings instance
settings = Settings()
