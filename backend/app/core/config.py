from pydantic_settings import BaseSettings
from typing import Optional
from pathlib import Path


class Settings(BaseSettings):
    # App
    APP_NAME: str = "Urban-Infra API"
    VERSION: str = "0.1.0"
    DEBUG: bool = False
    
    # Database - Prioritize DATABASE_URL for Supabase
    DATABASE_URL: Optional[str] = None
    DB_HOST: str = "localhost"
    DB_PORT: int = 5434
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "password"
    DB_NAME: str = "urban_infra"
    
    # Supabase specific
    SUPABASE_URL: Optional[str] = None
    SUPABASE_ANON_KEY: Optional[str] = None
    SUPABASE_SERVICE_ROLE_KEY: Optional[str] = None
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    
    # OpenAI
    OPENAI_API_KEY: Optional[str] = None
    
    # CORS - Updated for production
    ALLOWED_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:8000"]
    
    @property
    def db_url(self) -> str:
        # Always prioritize DATABASE_URL (for Supabase and production)
        if self.DATABASE_URL:
            return self.DATABASE_URL
        # Fallback to local PostgreSQL for development
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    @property
    def is_production(self) -> bool:
        return self.SUPABASE_URL is not None
    
    class Config:
        env_file = Path(__file__).parent.parent.parent.parent / ".env"  # Go up to project root
        env_file_encoding = "utf-8"


settings = Settings()