"""
Application Settings

Centralized configuration management using Pydantic.
"""
from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database
    # IMPORTANT: Always set DATABASE_URL in .env file
    DATABASE_URL: str
    POSTGRES_PASSWORD: Optional[str] = None

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # JWT Authentication
    # IMPORTANT: Always set JWT_SECRET_KEY in .env file
    # Generate with: openssl rand -hex 32
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Astrology Calculator
    CALCULATOR_PROVIDER: str = "kerykeion"
    DEFAULT_HOUSE_SYSTEM: str = "placidus"
    ORB_CONJUNCTION: float = 8.0
    ORB_OPPOSITION: float = 8.0
    ORB_TRINE: float = 8.0
    ORB_SQUARE: float = 7.0
    ORB_SEXTILE: float = 6.0
    ORB_SEMISQUARE: float = 3.0
    ORB_SESQUIQUADRATE: float = 3.0
    ORB_QUINCUNX: float = 3.0

    # Storage
    STORAGE_PROVIDER: str = "local"
    STORAGE_PATH: str = "/app/storage"
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_REGION: Optional[str] = None
    S3_BUCKET: Optional[str] = None

    # Chart Interpreter
    INTERPRETER_PROVIDER: str = "rule_based"
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None

    # Application
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "info"
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:5000,http://localhost"

    # Frontend
    REACT_APP_API_URL: str = "http://localhost:8000"
    REACT_APP_ENVIRONMENT: str = "development"
    REACT_APP_DEFAULT_LANGUAGE: str = "en"

    # Email (Optional)
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: Optional[int] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAIL_FROM: Optional[str] = None

    # Monitoring (Optional)
    SENTRY_DSN: Optional[str] = None
    SENTRY_ENVIRONMENT: Optional[str] = None

    # Rate Limiting (Optional)
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_PER_HOUR: int = 1000

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.

    Returns:
        Settings instance loaded from environment
    """
    return Settings()
