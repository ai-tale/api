import os
import secrets
from typing import List, Optional, Union
from pydantic import BaseSettings, PostgresDsn, validator

class Settings(BaseSettings):
    # API Settings
    API_ENV: str = "development"
    API_PREFIX: str = "/api/v1"
    DEBUG: bool = True
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    
    # CORS Settings
    CORS_ORIGINS: List[str] = ["*"]
    
    # Database Settings
    DATABASE_URL: PostgresDsn
    
    @validator("DATABASE_URL", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: dict) -> Any:
        if isinstance(v, str):
            return v
        return PostgresDsn.build(
            scheme="postgresql",
            user=os.getenv("POSTGRES_USER", "postgres"),
            password=os.getenv("POSTGRES_PASSWORD", "postgres"),
            host=os.getenv("POSTGRES_HOST", "localhost"),
            port=os.getenv("POSTGRES_PORT", "5432"),
            path=f"/{os.getenv('POSTGRES_DB', 'aitale')}",
        )
    
    # OpenAI Settings
    OPENAI_API_KEY: str
    OPENAI_ORG_ID: Optional[str] = None
    
    # Story Generation Settings
    STORY_GEN_MODEL: str = "gpt-4-turbo"
    MAX_STORY_LENGTH: int = 5000
    DEFAULT_LANGUAGE: str = "en"
    AVAILABLE_LANGUAGES: List[str] = ["en", "es", "fr", "de", "zh", "ja"]
    
    # Image Generation Settings
    IMAGE_GEN_MODEL: str = "dall-e-3"
    IMAGE_SIZE: str = "1024x1024"
    IMAGE_QUALITY: str = "standard"
    
    # AWS Settings
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_REGION: str = "us-west-2"
    S3_BUCKET: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Create settings instance
settings = Settings()

# Fix DATABASE_URL import issue
from typing import Any 