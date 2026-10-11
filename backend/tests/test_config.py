import pytest
from app.core.config import Settings


def test_settings_defaults():
    settings = Settings()
    assert settings.PROJECT_NAME == "e-BIS Sahayak"
    assert settings.VERSION == "0.1.0"
    assert settings.API_V1_STR == "/api/v1"
    assert len(settings.BACKEND_CORS_ORIGINS) >= 1
    assert "http://localhost:3000" in settings.BACKEND_CORS_ORIGINS


def test_development_allows_unconfigured_secrets():
    settings = Settings(ENVIRONMENT="development", GROQ_API_KEY="", ADMIN_API_KEY="")
    # Should not raise in development
    settings.validate_production_readiness()


def test_production_fails_when_secrets_missing():
    settings = Settings(ENVIRONMENT="production", GROQ_API_KEY="", ADMIN_API_KEY="")
    with pytest.raises(RuntimeError) as exc_info:
        settings.validate_production_readiness()
    assert "GROQ_API_KEY" in str(exc_info.value)
    assert "ADMIN_API_KEY" in str(exc_info.value)


def test_production_fails_when_secrets_are_placeholders():
    settings = Settings(
        ENVIRONMENT="production",
        GROQ_API_KEY="gsk_your_production_groq_api_key_here",
        ADMIN_API_KEY="your_admin_secret_key_here"
    )
    with pytest.raises(RuntimeError) as exc_info:
        settings.validate_production_readiness()
    assert "Production startup failed" in str(exc_info.value)


def test_production_passes_when_valid_secrets_configured():
    settings = Settings(
        ENVIRONMENT="production",
        GROQ_API_KEY="gsk_valid_configured_server_key_for_prod",
        ADMIN_API_KEY="prod-strong-random-admin-token-2026",
        DATABASE_URL="postgresql+asyncpg://prod_user:SecureProdPassword2026!@db.internal:5432/ebis_sahayak"
    )
    # Should pass without raising
    settings.validate_production_readiness()

