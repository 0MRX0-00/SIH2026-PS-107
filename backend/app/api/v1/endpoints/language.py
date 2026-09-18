from fastapi import APIRouter, Depends
from app.schemas.language import (
    LanguageDetectRequest,
    LanguageDetectResponse,
    SupportedLanguagesResponse
)
from app.services.language_service import LanguageService

router = APIRouter()

def get_language_service() -> LanguageService:
    return LanguageService()

@router.post("/detect", response_model=LanguageDetectResponse)
def detect_query_language(
    request: LanguageDetectRequest,
    service: LanguageService = Depends(get_language_service)
):
    """
    Detect the natural language and script of input text (English, Hindi, or Tamil).
    """
    lang_code, confidence, script = service.detect_language(request.text)
    is_supported = lang_code in ["en", "hi", "ta"]
    return LanguageDetectResponse(
        detected_language=lang_code,
        confidence=confidence,
        script=script,
        is_supported=is_supported
    )

@router.get("/supported", response_model=SupportedLanguagesResponse)
def list_supported_languages(
    service: LanguageService = Depends(get_language_service)
):
    """
    List all supported languages, scripts, and native display names.
    """
    return service.get_supported_languages()
