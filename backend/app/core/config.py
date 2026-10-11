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
        "http://localhost:8000",
        "http://127.0.0.1:8000"
    ]

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            v_trimmed = v.strip()
            if v_trimmed.startswith("[") and v_trimmed.endswith("]"):
                try:
                    import json
                    parsed = json.loads(v_trimmed)
                    if isinstance(parsed, list):
                        return [str(i).strip() for i in parsed if str(i).strip()]
                except Exception:
                    pass
            return [i.strip() for i in v_trimmed.split(",") if i.strip()]
        elif isinstance(v, list):
            return [str(i).strip() for i in v if str(i).strip()]
        return ["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:8000", "http://127.0.0.1:8000"]

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

    # Conversation Context
    MAX_CHAT_MESSAGE_LENGTH: int = 1000
    MAX_CONVERSATION_HISTORY_TURNS: int = 6

    # Official Source Evidence Lookup
    OFFICIAL_SOURCE_TIMEOUT_SECONDS: float = 5.0
    OFFICIAL_SOURCE_CACHE_TTL_SECONDS: int = 3600
    OFFICIAL_SOURCE_MAX_CACHE_ENTRIES: int = 500
    OFFICIAL_SOURCE_MAX_CONCURRENT: int = 3
    OFFICIAL_SOURCE_RATE_LIMIT_PER_MINUTE: int = 30

    # Security & Rate Limiting
    ADMIN_API_KEY: str = ""
    DEMO_MODE: bool = False
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_DEFAULT_PER_MINUTE: int = 120
    RATE_LIMIT_CHAT_PER_MINUTE: int = 40
    MAX_REQUEST_BODY_SIZE_BYTES: int = 2 * 1024 * 1024  # 2MB

    def validate_production_readiness(self) -> None:
        """Validates that production environment has all mandatory secrets and secure credentials configured."""
        if self.ENVIRONMENT.lower() == "production":
            missing_secrets = []
            if not self.GROQ_API_KEY or self.GROQ_API_KEY.startswith("gsk_your_") or self.GROQ_API_KEY == "your_groq_api_key_here":
                missing_secrets.append("GROQ_API_KEY")
            if not self.ADMIN_API_KEY or self.ADMIN_API_KEY.startswith("your_") or self.ADMIN_API_KEY == "your_admin_secret_key_here":
                missing_secrets.append("ADMIN_API_KEY")
            
            # Check for weak or default database credentials in production
            insecure_db_patterns = ["postgres:postgres@", ":password@", ":your_postgres_password_here@", ":postgres@"]
            if any(pat in self.DATABASE_URL for pat in insecure_db_patterns):
                missing_secrets.append("DATABASE_URL (configured with insecure default password)")

            if missing_secrets:
                raise RuntimeError(
                    f"Production startup failed: The following mandatory secrets are missing, unconfigured, or using insecure defaults: {', '.join(missing_secrets)}"
                )


settings = Settings()

