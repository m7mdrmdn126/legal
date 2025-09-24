from pydantic import BaseModel
from typing import Optional, List
import os

class Settings(BaseModel):
    """Application settings"""
    
    # App settings
    app_name: str = "Legal Cases Management System"
    app_version: str = "1.0.0"
    debug: bool = True
    
    # Security settings
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_hours: int = 12
    
    # Database settings
    database_path: str = "../database/legal_cases.db"
    
    # Network settings
    host: str = "127.0.0.1"  # Default to localhost, can be overridden
    port: int = 8000
    
    # Pagination settings
    default_page_size: int = 40
    max_page_size: int = 1000  # Increased to accommodate large datasets
    
    # Date format settings
    date_calendar: str = "gregorian"  # Use Gregorian (ميلادي) calendar
    date_locale: str = "ar-SA"        # Arabic locale with Gregorian calendar
    
    # CORS settings
    cors_origins: List[str] = ["http://localhost:3000", "http://localhost:8080"]
    
    def __init__(self, **kwargs):
        # Load from environment variables
        super().__init__(**kwargs)
        
        # Override with environment variables if they exist
        self.app_name = os.getenv("APP_NAME", self.app_name)
        self.app_version = os.getenv("APP_VERSION", self.app_version)
        self.debug = os.getenv("DEBUG", "true").lower() == "true"
        self.secret_key = os.getenv("SECRET_KEY", self.secret_key)
        self.algorithm = os.getenv("ALGORITHM", self.algorithm)
        self.access_token_expire_hours = int(os.getenv("ACCESS_TOKEN_EXPIRE_HOURS", self.access_token_expire_hours))
        self.database_path = os.getenv("DATABASE_PATH", self.database_path)
        
        # Network settings
        self.host = os.getenv("HOST", self.host)
        self.port = int(os.getenv("PORT", self.port))
        
        self.default_page_size = int(os.getenv("DEFAULT_PAGE_SIZE", self.default_page_size))
        self.max_page_size = int(os.getenv("MAX_PAGE_SIZE", self.max_page_size))
        
        # Parse CORS origins from environment
        cors_env = os.getenv("CORS_ORIGINS")
        if cors_env:
            self.cors_origins = [origin.strip() for origin in cors_env.split(",")]

# Global settings instance
settings = Settings()
