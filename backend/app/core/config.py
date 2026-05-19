"""
YAMA AI — Core Configuration
Loads environment variables and provides app-wide settings.
"""

import os
from pydantic_settings import BaseSettings
from typing import List, Optional
import json

# Default to SQLite so the backend runs out-of-the-box without PostgreSQL
_DEFAULT_DB = "sqlite:///./yama_ai.db"


class Settings(BaseSettings):
    # App
    APP_NAME: str = "YAMA AI"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # Database — defaults to SQLite; set to postgres:// for production
    DATABASE_URL: str = _DEFAULT_DB

    # LLM — set to "none" to use the built-in standalone analyzer
    LLM_PROVIDER: str = "none"  # none, openai, anthropic, ollama, gemini

    # OpenAI
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4"

    # Anthropic
    ANTHROPIC_API_KEY: Optional[str] = None
    ANTHROPIC_MODEL: str = "claude-3-sonnet-20240229"

    # Ollama
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "mistral"

    # Google Gemini
    GOOGLE_API_KEY: Optional[str] = None
    GEMINI_MODEL: str = "gemini-1.5-flash"

    # ChromaDB
    CHROMA_PERSIST_DIR: str = "./chroma_data"

    # CORS
    CORS_ORIGINS: str = '["http://localhost:3000", "http://localhost:3001"]'

    @property
    def cors_origins_list(self) -> List[str]:
        return json.loads(self.CORS_ORIGINS)

    @property
    def is_sqlite(self) -> bool:
        return self.DATABASE_URL.startswith("sqlite")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
