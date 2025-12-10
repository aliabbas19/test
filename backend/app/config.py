"""
Application configuration settings
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Application
    APP_NAME: str = "Basam Al Janaby Platform"
    APP_VERSION: str = "2.0.0"
    DEBUG: bool = False
    
    # Backend URL for file serving
    BACKEND_URL: str = "http://localhost:8000"
    
    # Database
    DATABASE_URL: str
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10
    
    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # AWS
    AWS_REGION: str = "me-south-1"
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    S3_BUCKET_NAME: str = "basamaljanaby-media"
    CLOUDFRONT_DOMAIN: Optional[str] = None
    
    # CORS
    CORS_ORIGINS: list[str] = ["https://basamaljanaby.com", "http://localhost:3000", "http://localhost:5173"]
    
    # File Upload
    MAX_UPLOAD_SIZE_MB: int = 200
    ALLOWED_IMAGE_EXTENSIONS: set[str] = {"png", "jpg", "jpeg", "gif"}
    ALLOWED_VIDEO_EXTENSIONS: set[str] = {"mp4", "mov", "avi"}
    UPLOAD_FOLDER: str = "uploads"  # Local storage fallback
    
    # Video Limits
    VIDEO_MAX_DURATION_MANHAJI: int = 60  # seconds
    VIDEO_MAX_DURATION_ITHRAI: int = 240  # seconds
    
    # Archive
    VIDEO_ARCHIVE_DAYS: int = 7
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 100
    
    # Telegram
    TELEGRAM_BOT_TOKEN: Optional[str] = None
    TELEGRAM_CHAT_ID: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
