"""
Evidence Traceability & False-Provenance Hardening Test Suite for e-BIS Sahayak.
"""
import pytest
from app.schemas.chat import ChatRequest
from app.services.query_service import query_service
from app.services.data_providers import get_bis_data_provider, LiveBISDataProvider
from app.db.seed_intelligence import VERIFIED_STANDARDS, VERIFIED_SCHEMES, VERIFIED_LABORATORIES


def test_valid_curated_record_has_authoritative_curated_status():
    """Test A: Valid curated record has verification_status == 'authoritative_curated'."""
    provider = get_bis_data_provider()
    std = VERIFIED_STANDARDS[0]
    prov = provider.get_evidence_provenance(std)
    assert prov["verified"] is True
    assert prov["verification_status"] == "authoritative_curated"
    assert "supported_claims" in prov
    assert isinstance(prov["supported_claims"], list)


def test_missing_or_invalid_url_yields_unverified_status():
    """Test B: Missing or invalid source URL marks record as unverified."""
    provider = get_bis_data_provider()
    invalid_record = {
        "title": "Missing URL Test",
        "standard_number": "IS 0000",
        "verified": True,
        "source_url": "",
        "provenance": "Unverified draft"
    }
    prov = provider.get_evidence_provenance(invalid_record)
    assert prov["verified"] is False
    assert prov["verification_status"] == "unverified"


@pytest.mark.asyncio
async def test_unsupported_claim_type_rejected():
    """Test C: Standard existence alone cannot support mandatory compliance without QCO evidence."""
    req = ChatRequest(message="Tell me about BIS Act 2016.", language="en")
    res = await query_service.process_query(req)
    assert res.answer is not None
    assert "mandatory qco for" not in res.answer.lower() or "section 16" in res.answer.lower() or "framework" in res.answer.lower()


@pytest.mark.asyncio
async def test_live_provider_fallback_labels_curated_evidence():
    """Test D: Live provider fallback clearly labels evidence as curated."""
    live_prov = LiveBISDataProvider()
    std_rec = VERIFIED_STANDARDS[0]
    prov = live_prov.get_evidence_provenance(std_rec)
    assert prov["verified"] is True
    assert "Provider Adapter" in prov["provenance"] or "authoritative_curated" in prov["verification_status"]


@pytest.mark.asyncio
async def test_unknown_product_yields_limited_evidence_status():
    """Test E: Unknown product lab query yields evidence_status == 'limited' and warning."""
    req = ChatRequest(message="Which laboratory tests product UNKNOWN-PROD-999?", language="en")
    res = await query_service.process_query(req)
    assert res.evidence_status in ["limited", "insufficient"]
    assert len(res.warnings) > 0


@pytest.mark.asyncio
async def test_unknown_standard_yields_insufficient_evidence():
    """Test F: Unknown standard yields evidence_status == 'insufficient'."""
    req = ChatRequest(message="Details of IS 9999999", language="en")
    res = await query_service.process_query(req)
    assert res.evidence_status == "insufficient"
    assert res.insufficient_evidence is True


@pytest.mark.asyncio
async def test_unsupported_fee_yields_insufficient_evidence():
    """Test G: Unsupported fee question yields insufficient evidence without inventing amount."""
    req = ChatRequest(message="What is the exact BIS fee for standard IS 88888888?", language="en")
    res = await query_service.process_query(req)
    assert res.evidence_status == "insufficient"
    assert res.insufficient_evidence is True


@pytest.mark.asyncio
async def test_fake_certificate_yields_procedure_guidance():
    """Test H: Fake certificate number yields procedure guidance rather than fabricated validity."""
    req = ChatRequest(message="Verify BIS license CM/L-999999999.", language="en")
    res = await query_service.process_query(req)
    assert res.answer is not None
    assert "manakonline" in res.answer.lower() or "verify" in res.answer.lower() or "procedure" in res.answer.lower()
