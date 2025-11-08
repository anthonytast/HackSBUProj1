from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Application
    app_name: str = "Study Planner API"
    app_version: str = "1.0.0"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    debug: bool = True
    
    # Canvas
    canvas_url: str = ""
    canvas_access_token: str = ""
    
    # Google Gemini
    gemini_api_key: str = ""
    
    # Google Calendar
    google_credentials_path: str = "credentials.json"
    google_token_path: str = "token.json"
    
    # Timezone
    timezone: str = "America/New_York"
    
    # CORS
    cors_origins: list = ["*"]
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance
    
    Returns:
        Settings object
    """
    return Settings()
