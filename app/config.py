from pydantic_settings import BaseSettings
from typing import List, Optional
import os


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql://postgres:your_password@localhost:5432/product_importer"
    
    # Redis (Heroku Redis sets REDIS_URL automatically)
    redis_url: str = "redis://localhost:6379/0"
    
    # Security
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Application
    debug: bool = True
    environment: str = "development"
    allowed_hosts: str = "localhost,127.0.0.1"  # Changed to string to avoid parsing issues
    max_file_size: int = 100 * 1024 * 1024  # 100MB
    upload_dir: str = "uploads"
    
    # Celery (Use REDIS_URL if available, fallback to redis_url)
    celery_broker_url: Optional[str] = None
    celery_result_backend: Optional[str] = None
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Use REDIS_URL for Celery if available (Heroku sets this)
        redis_url = os.getenv("REDIS_URL", self.redis_url)
        if not self.celery_broker_url:
            self.celery_broker_url = redis_url
        if not self.celery_result_backend:
            self.celery_result_backend = redis_url
    
    class Config:
        env_file = ".env"
    
    def get_allowed_hosts_list(self) -> List[str]:
        """Convert allowed_hosts string to list"""
        return [host.strip() for host in self.allowed_hosts.split(",")]


# Create global settings instance
settings = Settings()