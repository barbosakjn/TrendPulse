"""
Application configuration using Pydantic settings.
"""
from pydantic_settings import BaseSettings
from typing import Optional, List
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    APP_NAME: str = "TrendPulse"
    APP_VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api"
    NEXT_PUBLIC_APP_URL: str = "http://localhost:3000"
    DEBUG: bool = False

    # Database
    DATABASE_URL: str = "postgresql://trendpulse:password@localhost:5432/trendpulse"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"

    # Security
    SECRET_KEY: str = "change-this-secret-key-in-production"
    JWT_SECRET_KEY: str = "change-this-jwt-secret-key-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:8000",
    ]

    # Email
    EMAIL_PROVIDER: str = "resend"  # resend or sendgrid
    RESEND_API_KEY: Optional[str] = None
    SENDGRID_API_KEY: Optional[str] = None
    EMAIL_FROM: str = "noreply@trendpulse.com"
    EMAIL_FROM_NAME: str = "TrendPulse"

    # External APIs
    YOUTUBE_API_KEY: Optional[str] = None
    YOUTUBE_QUOTA_LIMIT: int = 10000
    REDDIT_CLIENT_ID: Optional[str] = None
    REDDIT_CLIENT_SECRET: Optional[str] = None
    REDDIT_USER_AGENT: str = "TrendPulse/1.0"
    EXA_API_KEY: Optional[str] = None

    # OAuth
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None
    GITHUB_CLIENT_ID: Optional[str] = None
    GITHUB_CLIENT_SECRET: Optional[str] = None

    # Data Collection
    COLLECTION_INTERVAL_HOURS: int = 6
    TRENDING_CACHE_TTL_SECONDS: int = 21600  # 6 hours
    MAX_TRENDS_PER_COLLECTION: int = 500

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 100
    RATE_LIMIT_ENABLED: bool = True

    # Monitoring
    SENTRY_DSN: Optional[str] = None
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"  # Relative to backend/ directory (working directory)
        case_sensitive = True
        extra = "ignore"  # Ignore extra fields not defined in Settings


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.
    Using lru_cache ensures settings are loaded only once.
    """
    return Settings()


# Global settings instance
settings = get_settings()
