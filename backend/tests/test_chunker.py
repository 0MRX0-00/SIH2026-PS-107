from app.services.chunker import StructureAwareChunker
from app.services.document_parser import ExtractedPage


def test_structure_aware_chunker():
    chunker = StructureAwareChunker(target_chunk_size=500, min_chunk_size=50)

    sample_pages = [
        ExtractedPage(
            page_number=1,
            text="Section 5 — Requirements\n\nClause 5.1 — Insulation\nAll current-carrying conductors shall be insulated with high-grade polymer.\n\nClause 5.2 — Clearances\nCreepage distances shall be not less than 6.0 mm."
        ),
        ExtractedPage(
            page_number=2,
            text="Clause 5.3 — Shutters\nAutomatic shutters are mandatory on all live contacts."
        )
    ]

    doc_meta = {
        "document_id": "test-doc-001",
        "standard_number": "IS 1293:2019",
        "title": "Plugs and Socket-Outlets",
        "source_name": "BIS Test"
    }

    chunks = chunker.chunk_pages(sample_pages, doc_meta)
    assert len(chunks) >= 2

    # Check contextual header preservation
    assert "IS 1293:2019" in chunks[0].text
    assert "Page 1" in chunks[0].text
    assert chunks[0].standard_number == "IS 1293:2019"
    assert chunks[0].page_start == 1
    assert chunks[-1].page_start == 2
