from app.core.config import Settings


def test_settings_defaults():
    settings = Settings()
    assert settings.PROJECT_NAME == "e-BIS Sahayak"
    assert settings.VERSION == "0.1.0"
    assert settings.API_V1_STR == "/api/v1"
    assert len(settings.BACKEND_CORS_ORIGINS) >= 1
    assert "http://localhost:3000" in settings.BACKEND_CORS_ORIGINS
