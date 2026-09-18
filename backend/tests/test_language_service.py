import pytest
from app.services.language_service import LanguageService


@pytest.fixture
def lang_service():
    return LanguageService()


def test_detect_english(lang_service):
    lang, conf, script = lang_service.detect_language("What are the temperature rise requirements in IS 1293?")
    assert lang == "en"
    assert script == "Latin"
    assert conf >= 0.8


def test_detect_hindi(lang_service):
    lang, conf, script = lang_service.detect_language("IS 1293 के तहत तापमान वृद्धि की आवश्यकताएं क्या हैं?")
    assert lang == "hi"
    assert script == "Devanagari"
    assert conf >= 0.8


def test_detect_tamil(lang_service):
    lang, conf, script = lang_service.detect_language("IS 1293 இன் கீழ் வெப்பநிலை அதிகரிப்பு தேவைகள் என்ன?")
    assert lang == "ta"
    assert script == "Tamil"
    assert conf >= 0.8


def test_normalize_and_translate_for_retrieval(lang_service):
    # Hindi cross-lingual retrieval
    en_query = lang_service.normalize_and_translate_for_retrieval(
        "प्रेशर कुकर के लिए कौन सा मानक लागू होता है?", "hi"
    )
    assert "pressure cooker" in en_query.lower()

    # Tamil cross-lingual retrieval
    ta_query = lang_service.normalize_and_translate_for_retrieval(
        "மின்விசிறி மற்றும் ஃபேன் சோதனை ஆய்வகம்", "ta"
    )
    assert "ceiling fan" in ta_query.lower() or "fan" in ta_query.lower()


def test_supported_languages(lang_service):
    res = lang_service.get_supported_languages()
    assert len(res.languages) == 3
    codes = [l.code for l in res.languages]
    assert "en" in codes
    assert "hi" in codes
    assert "ta" in codes
