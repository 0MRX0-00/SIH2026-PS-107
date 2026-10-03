from typing import List, Union
from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # Application Metadata
    ENVIRONMENT: str = "development"
    PROJECT_NAME: str = "e-BIS Sahayak"
    VERSION: str = "0.1.0"
    PHASE: str = "Production Groq AI Assistant Engine"
    API_V1_STR: str = "/api/v1"

    # CORS Configuration
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000"
    ]

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, list):
            return v
        return ["http://localhost:3000", "http://127.0.0.1:3000"]

    # PostgreSQL Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/ebis_sahayak"
    DATABASE_SYNC_URL: str = "postgresql://postgres:postgres@localhost:5432/ebis_sahayak"

    # Groq LLM Configuration
    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "llama-3.3-70b-versatile"
    GROQ_BASE_URL: str = "https://api.groq.com/openai/v1"
    GROQ_TIMEOUT_SECONDS: float = 30.0
    GROQ_MAX_TOKENS: int = 1500
    GROQ_TEMPERATURE: float = 0.1

    # Conversation Context & RAG Thresholds
    MAX_CHAT_MESSAGE_LENGTH: int = 1000
    MAX_CONVERSATION_HISTORY_TURNS: int = 6
    RAG_MIN_RELEVANCE_SCORE: float = 0.65

    # Security & Rate Limiting
    ADMIN_API_KEY: str = "ebis-admin-secret-key-2026"
    DEMO_MODE: bool = False
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_DEFAULT_PER_MINUTE: int = 120
    RATE_LIMIT_CHAT_PER_MINUTE: int = 40
    MAX_REQUEST_BODY_SIZE_BYTES: int = 2 * 1024 * 1024  # 2MB


settings = Settings()
