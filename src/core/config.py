"""
Application Configuration

Loads and manages all configuration settings from environment variables.
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # Gemini API Configuration (OpenAI-compatible endpoint)
    gemini_base_url: str = "https://solid-cloths-search.loca.lt/v1"
    gemini_api_key: str = "sk-2be085140ff24a9eb28fafc66f25db49"
    gemini_model: str = "gemini-3-flash"

    # Embedding Configuration
    embedding_model: str = "all-MiniLM-L6-v2"
    embedding_dimension: int = 384

    # API Configuration
    api_version: str = "v1"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    log_level: str = "INFO"

    # Application Settings
    max_query_results: int = 10
    similarity_threshold: float = 0.7
    default_timezone: str = "UTC"

    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
