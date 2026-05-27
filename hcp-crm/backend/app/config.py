"""
Application configuration using pydantic-settings.
Reads from environment variables or .env file.
"""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://postgres:password@localhost:5432/hcp_crm"

    # Groq API
    GROQ_API_KEY: str = ""
    PRIMARY_MODEL: str = "gemma2-9b-it"
    FALLBACK_MODEL: str = "llama-3.3-70b-versatile"

    # App
    APP_NAME: str = "HCP CRM"
    DEBUG: bool = True
    CORS_ORIGINS: list = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001",
    ]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


def get_settings() -> Settings:
    """Return application settings. Re-reads .env on every call during development."""
    return Settings()
