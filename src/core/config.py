"""
Application Configuration

This module manages all configuration settings, loading from environment
variables with sensible defaults.
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # Gemini API Configuration
    gemini_api_key: str
    gemini_model: str = "gemini-flash"

    # Database Configuration
    database_url: str
    chroma_host: str = "localhost"
    chroma_port: int = 8000
    chroma_collection: str = "workout_memories"

    # Embedding Configuration
    embedding_model: str = "all-MiniLM-L6-v2"
    embedding_dimension: int = 384

    # API Configuration
    api_version: str = "v1"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    log_level: str = "INFO"

    # Security
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # Application Settings
    max_query_results: int = 10
    similarity_threshold: float = 0.7
    default_timezone: str = "UTC"

    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
