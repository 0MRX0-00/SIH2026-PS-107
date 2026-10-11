"""
Comprehensive Test Suite for e-BIS Sahayak Standards Explorer & Repository.
Validates:
1. Exact catalogue integrity, statutory Indian Standards count, and division distribution.
2. Complete provenance metadata on every standard (source_url, authority, verified status, last_verified date).
3. Separation of genuine Indian Standards from general Acts/QCOs/schemes.
4. Search by IS number, title, keywords, technical division, product category, and QCO mandatory status.
5. Multilingual translations in English, Hindi (hi), and Tamil (ta).
6. Prevention of duplicate standards and safe handling of non-existent/unverified lookups.
7. Standards service and REST API endpoint validation.
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db.standards_data import OFFICIAL_INDIAN_STANDARDS, STATUTORY_REGULATORY_REFERENCES
from app.db.seed_intelligence import (
    VERIFIED_STANDARDS,
    get_localized_standard,
    get_localized_all_standards
)
from app.services.standards_service import standards_service
from app.services.data_providers import get_bis_data_provider


client = TestClient(app)


def test_catalogue_count_and_is_prefix_integrity():
    """Verify that all records in VERIFIED_STANDARDS are genuine Indian Standards (IS prefix)."""
    assert len(VERIFIED_STANDARDS) >= 20
    assert len(VERIFIED_STANDARDS) == len(OFFICIAL_INDIAN_STANDARDS)

    for std in VERIFIED_STANDARDS:
        std_num = std["standard_number"]
        assert std_num.startswith("IS") or "IS/" in std_num, f"Invalid standard number: {std_num}"
        assert std["title"] is not None and len(std["title"]) > 10
        assert std["division"] in [
            "Electrotechnical",
            "Electronics & Information Technology",
            "Civil Engineering",
            "Food and Agriculture",
            "Mechanical Engineering & Consumer Products",
            "Metallurgical Engineering",
            "Chemical Engineering",
            "Medical Equipment & Healthcare"
        ], f"Invalid division: {std['division']}"


def test_statutory_administrative_separation():
    """Verify that Acts, general schemes, and general QCO guides are not in VERIFIED_STANDARDS."""
    standard_ids = [s["id"] for s in VERIFIED_STANDARDS]
    assert "std-bis-act" not in standard_ids
    assert "std-qco-guide" not in standard_ids
    assert "std-scheme-isi" not in standard_ids

    assert "BIS_ACT_2016" in STATUTORY_REGULATORY_REFERENCES
    assert "CONFORMITY_ASSESSMENT_REGS_2018" in STATUTORY_REGULATORY_REFERENCES
    assert "QCO_FRAMEWORK" in STATUTORY_REGULATORY_REFERENCES


def test_provenance_metadata_completeness_on_all_standards():
    """Verify that every standard has complete provenance metadata and valid BIS URLs."""
    provider = get_bis_data_provider()

    for std in VERIFIED_STANDARDS:
        prov = provider.get_evidence_provenance(std)
        assert prov["verified"] is True
        assert prov["verification_status"] == "authoritative_verified"
        assert prov["authority"] == "Bureau of Indian Standards"
        assert prov["source_type"] == "official_bis"
        assert prov["source_url"].startswith("http")
        assert "bis.gov.in" in prov["source_url"] or "manakonline.in" in prov["source_url"]
        assert prov["last_verified"] is not None


def test_unique_standard_numbers_no_duplicates():
    """Verify there are zero duplicate standard numbers or IDs in the registry."""
    std_numbers = [s["standard_number"] for s in VERIFIED_STANDARDS]
    std_ids = [s["id"] for s in VERIFIED_STANDARDS]

    assert len(std_numbers) == len(set(std_numbers)), "Duplicate standard numbers found"
    assert len(std_ids) == len(set(std_ids)), "Duplicate standard IDs found"


def test_search_by_standard_number():
    """Verify precise and partial search by standard number."""
    res_1293 = standards_service.search_standards(query="IS 1293")
    assert len(res_1293) >= 1
    assert any("1293" in s.standard_number for s in res_1293)

    res_13252 = standards_service.search_standards(query="13252")
    assert len(res_13252) >= 1
    assert any("13252" in s.standard_number for s in res_13252)

    res_456 = standards_service.search_standards(query="456")
    assert len(res_456) >= 1
    assert any("456" in s.standard_number for s in res_456)


def test_search_by_division_filter():
    """Verify filtering by technical division."""
    electro = standards_service.search_standards(division="Electrotechnical")
    assert len(electro) >= 5
    for s in electro:
        assert s.division == "Electrotechnical"

    civil = standards_service.search_standards(division="Civil Engineering")
    assert len(civil) >= 3
    for s in civil:
        assert s.division == "Civil Engineering"


def test_search_by_product_category():
    """Verify filtering by product category."""
    cables = standards_service.search_standards(product_category="Electrical Cables & Wires")
    assert len(cables) >= 1
    assert any("694" in s.standard_number for s in cables)

    cement = standards_service.search_standards(product_category="Cement & Building Materials")
    assert len(cement) >= 2
    assert any("12269" in s.standard_number for s in cement)


def test_search_by_qco_mandatory_flag():
    """Verify filtering for mandatory Quality Control Orders only."""
    qco_list = standards_service.search_standards(qco_only=True)
    assert len(qco_list) >= 15
    for s in qco_list:
        assert s.is_qco_mandatory is True
        assert s.qco_order_number is not None


def test_multilingual_localization_hindi_and_tamil():
    """Verify that Hindi and Tamil translations preserve accuracy without breaking fields."""
    hi_std = standards_service.get_standard_details("IS 1293:2019", language="hi")
    assert hi_std is not None
    assert "प्लग और सॉकेट-आउटलेट" in hi_std.title
    assert hi_std.division == "इलेक्ट्रो-तकनीकी"

    ta_std = standards_service.get_standard_details("IS 1293:2019", language="ta")
    assert ta_std is not None
    assert "பிளக்குகள்" in ta_std.title
    assert ta_std.division == "மின் தொழில்நுட்பம்"


def test_safe_handling_of_nonexistent_standard():
    """Verify that unknown standard lookups return None without fabricating details."""
    res = standards_service.get_standard_details("IS 9999999-FAKE")
    assert res is None

    api_res = client.get("/api/v1/standards/IS-9999999-FAKE")
    assert api_res.status_code == 404
    assert "not found" in api_res.json()["detail"].lower()


def test_standards_api_endpoint_list_and_details():
    """Verify the REST API endpoints /api/v1/standards/ and /api/v1/standards/{id}."""
    resp = client.get("/api/v1/standards/?division=Electrotechnical&qco_only=true")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) >= 4
    assert all(item["is_qco_mandatory"] is True for item in data)

    # Fetch details
    first_std_num = data[0]["standard_number"]
    detail_resp = client.get(f"/api/v1/standards/{first_std_num}")
    assert detail_resp.status_code == 200
    detail_data = detail_resp.json()
    assert detail_data["standard_number"] == first_std_num
    assert detail_data["source_url"] is not None
    assert "sections" in detail_data


def test_identifier_normalization_variations():
    """Verify that identifier lookups normalize punctuation, case, and spacing."""
    variations = ["IS 1293:2019", "is 1293", "IS-1293", "is1293", "1293"]
    for var in variations:
        res = standards_service.get_standard_details(var)
        assert res is not None, f"Failed lookup for variation: {var}"
        assert "1293" in res.standard_number


def test_empty_query_and_no_result_handling():
    """Verify empty query returns full active catalog and nonsense returns empty list."""
    all_res = standards_service.search_standards(query="")
    assert len(all_res) == len(OFFICIAL_INDIAN_STANDARDS)

    empty_res = standards_service.search_standards(query="xyz999nonexistentquerykeyword")
    assert len(empty_res) == 0


def test_qco_evidence_not_assumed_without_explicit_metadata():
    """Verify standards without mandatory QCO order number have is_qco_mandatory=False."""
    voluntary_stds = [s for s in OFFICIAL_INDIAN_STANDARDS if not s.get("is_qco_mandatory")]
    assert len(voluntary_stds) >= 1
    for s in voluntary_stds:
        assert s["is_qco_mandatory"] is False
        assert s.get("qco_order_number") is None

