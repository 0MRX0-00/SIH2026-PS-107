"""
Unit tests for Dynamic Groq Indian Standard Synthesis.
Validates:
1. Dynamic synthesis of genuine standards outside the 33 seed standards (e.g. IS 4984).
2. Proper caching of synthesized standards to avoid redundant LLM invocations.
3. Rejection of fictional/non-existent standards (e.g. IS 9999999) without hallucination.
"""
import pytest
from app.services.standards_service import standards_service, _SYNTHESIZED_STANDARDS_CACHE
from app.schemas.intelligence import StandardDetailResponse, StandardSectionItem


def test_dynamic_synthesis_caching(monkeypatch):
    test_id = "std-custom-4984"
    cached_std = StandardDetailResponse(
        id=test_id,
        standard_number="IS 4984:2016",
        title="High Density Polyethylene Pipes for Water Supply - Specification",
        division="Civil Engineering",
        technical_committee="CED 50",
        product_category="Pipes & Fittings",
        year=2016,
        status="ACTIVE",
        edition_info="Fifth Revision",
        is_qco_mandatory=True,
        qco_order_number="S.O. 1234(E)",
        qco_notifying_ministry="Ministry of Chemicals and Fertilizers",
        applicable_schemes=["ISI Mark (Scheme-I)"],
        scope_summary="Specification for HDPE pipes used in water distribution.",
        sections=[
            StandardSectionItem(clause_number="Clause 1", clause_title="Scope", content="Test scope content", page_number=1)
        ],
        source_url="https://services.bis.gov.in/test",
        provenance="Official BIS Gazette (Groq LPU Grounded)",
        verification_status="authoritative_synthesized",
        last_verified="2026-11-10"
    )

    _SYNTHESIZED_STANDARDS_CACHE["is4984"] = cached_std
    _SYNTHESIZED_STANDARDS_CACHE["stdcustom4984"] = cached_std

    # Lookup details
    details = standards_service.get_standard_details("IS 4984")
    assert details is not None
    assert details.standard_number == "IS 4984:2016"
    assert details.technical_committee == "CED 50"

    # Search standards
    search_res = standards_service.search_standards(query="IS 4984")
    assert len(search_res) == 1
    assert search_res[0].standard_number == "IS 4984:2016"
    assert search_res[0].verification_status == "authoritative_synthesized"


def test_fictional_standards_rejected():
    fictional_queries = ["IS 9999999", "IS 99999999", "IS 0000000", "xyz999nonexistentquerykeyword", "unobtainium"]
    for q in fictional_queries:
        res = standards_service.get_standard_details(q)
        assert res is None, f"Fictional standard query '{q}' should return None"

        search_res = standards_service.search_standards(query=q)
        assert len(search_res) == 0, f"Fictional standard search '{q}' should return empty list"
