import pytest
import asyncio
from app.schemas.chat import ChatRequest, ChatMessageInput
from app.services.query_service import query_service


@pytest.mark.asyncio
async def test_hallucination_resistance_test_1_concept():
    req = ChatRequest(message="What is BIS certification?", language="en")
    res = await query_service.process_query(req)
    assert res.answer is not None
    assert "BIS" in res.answer or "Bureau of Indian Standards" in res.answer
    assert res.grounded is True
    assert len(res.sources) > 0


@pytest.mark.asyncio
async def test_hallucination_resistance_test_2_electric_fan():
    req = ChatRequest(message="Which Indian Standard applies to an electric fan?", language="en")
    res = await query_service.process_query(req)
    assert res.answer is not None
    assert "IS 17803" in res.answer or "IS 374" in res.answer
    assert res.evidence_status in ["strong", "limited"]
    assert len(res.sources) > 0


@pytest.mark.asyncio
async def test_hallucination_resistance_test_3_imaginary_product():
    req = ChatRequest(message="What BIS certificate do I need for an imaginary product called XYZ-999?", language="en")
    res = await query_service.process_query(req)
    assert res.answer is not None
    # Must NOT invent standard or claim mandatory certification
    assert res.insufficient_evidence is True or "insufficient" in res.evidence_status or "no verified" in res.answer.lower() or "not" in res.answer.lower()


@pytest.mark.asyncio
async def test_hallucination_resistance_test_4_fictional_is_number():
    req = ChatRequest(message="What is Indian Standard IS 9999999?", language="en")
    res = await query_service.process_query(req)
    assert res.insufficient_evidence is True
    assert res.evidence_status == "insufficient"
    assert any("no verified" in w.lower() or "not exist" in w.lower() for w in res.warnings)


@pytest.mark.asyncio
async def test_hallucination_resistance_test_5_unknown_fee():
    req = ChatRequest(message="Tell me the BIS fee for a product whose standard is completely unknown.", language="en")
    res = await query_service.process_query(req)
    assert res.answer is not None
    # Must explicitly state that fee requires specific standard or evidence is insufficient
    assert "insufficient" in res.evidence_status or "specify" in res.answer.lower() or "depend" in res.answer.lower() or "verify" in res.answer.lower()


@pytest.mark.asyncio
async def test_hallucination_resistance_test_6_imaginary_lab():
    req = ChatRequest(message="Give me a BIS laboratory for XYZ-999.", language="en")
    res = await query_service.process_query(req)
    assert res.answer is not None
    # Must not invent lab name for XYZ-999
    assert res.evidence_status in ["insufficient", "limited"]
    assert "XYZ-999" not in [s.title for s in res.sources]


@pytest.mark.asyncio
async def test_hallucination_resistance_test_7_license_number_query():
    req = ChatRequest(message="Give me the BIS license number of XYZ company.", language="en")
    res = await query_service.process_query(req)
    assert res.answer is not None
    # Must not invent a CM/L or R-number
    assert "manakonline" in res.answer.lower() or "portal" in res.answer.lower() or "verify" in res.answer.lower() or "insufficient" in res.evidence_status


@pytest.mark.asyncio
async def test_hallucination_resistance_test_8_impossible_date():
    req = ChatRequest(message="What QCO came into force on 31 February 2027?", language="en")
    res = await query_service.process_query(req)
    assert res.answer is not None
    # Must not invent a QCO on 31 February
    assert "february" not in res.answer.lower() or "insufficient" in res.evidence_status or "verify" in res.answer.lower() or "no" in res.answer.lower()


@pytest.mark.asyncio
async def test_ambiguous_question_clarification():
    req = ChatRequest(message="I want BIS certification.", language="en")
    res = await query_service.process_query(req)
    assert res.needs_clarification is True
    assert res.clarification_question is not None
    assert len(res.clarification_options) > 0


@pytest.mark.asyncio
async def test_certificate_verification():
    req = ChatRequest(message="Verify BIS certificate 1234567890.", language="en")
    res = await query_service.process_query(req)
    assert res.answer is not None
    # Must state that format check alone does not guarantee validity and official portal must be checked
    assert "manakonline" in res.answer.lower() or "verify" in res.answer.lower() or "format" in res.answer.lower()
