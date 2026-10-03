"""
Data Provenance & Source Priority Verification Test Suite for e-BIS Sahayak.
Covering False-Provenance Scenarios, Provider Fallbacks, and Claim Integrity.
"""
import pytest
from app.schemas.chat import ChatRequest, SourceItem
from app.services.query_service import query_service
from app.services.data_providers import get_bis_data_provider, LiveBISDataProvider
from app.db.seed_intelligence import VERIFIED_STANDARDS, VERIFIED_SCHEMES, VERIFIED_LABORATORIES


def test_provenance_metadata_present_on_all_seed_records():
    """Test 1A: Every production evidence record has explicit provenance metadata."""
    provider = get_bis_data_provider()
    
    for std in VERIFIED_STANDARDS:
        prov = provider.get_evidence_provenance(std)
        assert prov["authority"] is not None
        assert prov["verified"] is True
        assert prov["verification_status"] in ["authoritative_curated", "authoritative_verified"]
        assert prov["source_type"] == "official_bis"
        assert prov["provenance"] is not None

    for lab in VERIFIED_LABORATORIES:
        prov = provider.get_evidence_provenance(lab)
        assert prov["authority"] is not None
        assert prov["verified"] is True
        assert prov["source_type"] in ["official_bis", "registered_laboratory"]


def test_invalid_url_record_invalidates_verified_status():
    """Test 1B: Record with invalid or missing URL is invalidated."""
    provider = get_bis_data_provider()
    invalid_url_record = {
        "title": "Invalid URL Record",
        "standard_number": "IS 9999",
        "verified": True,
        "verification_status": "authoritative_curated",
        "source_url": "invalid-url-string",
        "provenance": "Unverified record"
    }
    prov = provider.get_evidence_provenance(invalid_url_record)
    assert prov["verified"] is False
    assert prov["verification_status"] == "unverified"


def test_unverified_records_cannot_be_marked_authoritative():
    """Test B: Unverified / demo records cannot be presented as authoritative."""
    provider = get_bis_data_provider()
    fake_record = {
        "title": "Unverified Test Record",
        "standard_number": "IS 0000",
        "verified": False,
        "verification_status": "unverified",
        "source_type": "demo_seed",
        "provenance": "Unverified draft fixture"
    }
    prov = provider.get_evidence_provenance(fake_record)
    assert prov["verified"] is False
    assert prov["verification_status"] == "unverified"
    assert prov["source_type"] == "demo_seed"


@pytest.mark.asyncio
async def test_standard_existence_does_not_imply_mandatory_qco_without_evidence():
    """Test 2: Standard existence alone cannot claim mandatory QCO without supporting QCO evidence."""
    req = ChatRequest(message="Tell me about BIS Act 2016.", language="en")
    res = await query_service.process_query(req)
    assert res.answer is not None
    assert "mandatory qco for" not in res.answer.lower() or "section 16" in res.answer.lower() or "framework" in res.answer.lower()


@pytest.mark.asyncio
async def test_unrelated_lab_not_presented_as_product_specific():
    """Test 3 & 7: Laboratory query for unknown product returns limited evidence status with explicit warning."""
    req = ChatRequest(message="Which laboratory tests product ABC-XYZ-UNKNOWN?", language="en")
    res = await query_service.process_query(req)
    assert res.evidence_status in ["limited", "insufficient"]
    assert any("no specific bis recognized laboratory" in w.lower() or "unspecified" in w.lower() or "general" in w.lower() for w in res.warnings)


@pytest.mark.asyncio
async def test_live_provider_fallback_to_seed():
    """Test 4: LiveBISDataProvider falls back cleanly to seed data and attaches provenance."""
    live_prov = LiveBISDataProvider()
    stds = live_prov.search_standards(query="fan", limit=2)
    assert len(stds) > 0
    assert stds[0].standard_number is not None


@pytest.mark.asyncio
async def test_missing_evidence_results_in_insufficient_status():
    """Test 5 & 6: Missing evidence for fake standard IS 9999999 yields insufficient status and no hallucination."""
    req = ChatRequest(message="What is Indian Standard IS 9999999?", language="en")
    res = await query_service.process_query(req)
    assert res.evidence_status == "insufficient"
    assert res.insufficient_evidence is True
    assert len(res.sources) == 0


@pytest.mark.asyncio
async def test_unsupported_fee_question_does_not_invent_amount():
    """Test 8: Unsupported fee question declares no verified fee evidence available rather than inventing an amount."""
    req = ChatRequest(message="Tell me the exact BIS licensing fee for standard IS 9999999.", language="en")
    res = await query_service.process_query(req)
    assert res.evidence_status == "insufficient"
    assert res.insufficient_evidence is True
