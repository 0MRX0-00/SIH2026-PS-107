from pathlib import Path
from app.services.document_parser import DocumentParser, ExtractedPage
from app.services.document_loader import DocumentLoader


def test_document_loader_and_parser_markdown():
    sample_path = Path("..") / "data" / "sample" / "is_1293_plugs_sample.md"
    if not sample_path.exists():
        sample_path = Path("data") / "sample" / "is_1293_plugs_sample.md"

    # Validate loader
    inspection = DocumentLoader.validate_and_inspect(sample_path)
    assert inspection["extension"] == ".md"
    assert len(inspection["file_hash_sha256"]) == 64

    # Validate parser
    pages = DocumentParser.parse(sample_path)
    assert len(pages) >= 3
    assert pages[0].page_number == 1
    assert "IS 1293:2019" in pages[0].text
    assert "Section 1: Scope" in pages[0].text


def test_document_loader_text_fixture():
    sample_path = Path("..") / "data" / "sample" / "crs_electronics_sample.txt"
    if not sample_path.exists():
        sample_path = Path("data") / "sample" / "crs_electronics_sample.txt"

    pages = DocumentParser.parse(sample_path)
    assert len(pages) >= 2
    assert "COMPULSORY REGISTRATION SCHEME" in pages[0].text
