from pydantic_settings import BaseSettings
from typing import Optional, List
import os

class Settings(BaseSettings):
    # App
    app_name: str = "Financial Health Assessment Platform"
    debug: bool = False
    
    # Database
    database_url: str = "sqlite:///./financial_health.db"
    
    # Security
    secret_key: str = "dev-secret-key-change-in-production-12345"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    encryption_key: str = "dev-encryption-key-change-in-production-12345"
    
    # LLM
    openai_api_key: Optional[str] = None
    claude_api_key: Optional[str] = None
    llm_provider: str = "openai"  # openai or claude
    
    # Banking APIs
    bank_api_1_key: Optional[str] = None
    bank_api_1_secret: Optional[str] = None
    bank_api_2_key: Optional[str] = None
    bank_api_2_secret: Optional[str] = None
    
    # GST
    gst_api_key: Optional[str] = None
    
    class Config:
        env_file = os.path.join(os.path.dirname(__file__), "..", ".env")
        case_sensitive = False

settings = Settings()
