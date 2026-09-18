from typing import List, Optional
from pydantic import BaseModel, Field


class SupportedLanguageItem(BaseModel):
    code: str = Field(..., description="ISO 639-1 language code e.g. 'en', 'hi', 'ta'")
    name: str = Field(..., description="English name e.g. 'English', 'Hindi', 'Tamil'")
    native_name: str = Field(..., description="Native name e.g. 'English', 'हिन्दी', 'தமிழ்'")
    script: str = Field(..., description="Script name e.g. 'Latin', 'Devanagari', 'Tamil'")
    is_supported: bool = True


class SupportedLanguagesResponse(BaseModel):
    languages: List[SupportedLanguageItem]
    default_language: str = "en"


class LanguageDetectRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=2000, description="Input text to detect language for")


class LanguageDetectResponse(BaseModel):
    detected_language: str = Field(..., description="'en', 'hi', 'ta', or 'unsupported'")
    confidence: float = Field(..., ge=0.0, le=1.0)
    script: str
    is_supported: bool
