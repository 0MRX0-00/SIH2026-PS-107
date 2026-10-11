import pytest
from app.services.certification_navigator_service import CertificationNavigatorService
from app.schemas.intelligence import CertificationRoadmapRequest
from app.db.seed_intelligence import get_localized_all_schemes, get_localized_scheme, VERIFIED_SCHEMES


@pytest.fixture
def cert_service():
    return CertificationNavigatorService()


def test_roadmap_generation_by_standard(cert_service):
    request = CertificationRoadmapRequest(standard_number="IS 1293:2019")
    response = cert_service.generate_roadmap(request)
    assert response.standard_number == "IS 1293:2019"
    assert response.is_mandatory_qco is True
    assert len(response.steps) >= 5
    assert response.applicable_scheme in ("SCHEME_I_ISI_NORMAL", "SCHEME_I_ISI")
    assert "does not constitute official BIS approval" in response.disclaimer
    assert len(response.document_checklist) > 0
    assert len(response.official_sources) == 5


def test_roadmap_generation_by_it_equipment(cert_service):
    request = CertificationRoadmapRequest(standard_number="IS 13252")
    response = cert_service.generate_roadmap(request)
    assert response.applicable_scheme == "SCHEME_II_CRS"
    assert len(response.steps) >= 5
    assert any("Portal" in step.title or "CRS" in step.title for step in response.steps)


def test_roadmap_disclaimer_present(cert_service):
    request = CertificationRoadmapRequest(product_name="Electric Fans")
    response = cert_service.generate_roadmap(request)
    assert "does not constitute official BIS approval" in response.disclaimer
    assert response.route_rationale is not None


def test_roadmap_foreign_manufacturer_fmcs(cert_service):
    request = CertificationRoadmapRequest(
        product_name="Ceramic Tiles",
        country_of_manufacture="Germany",
        manufacturer_type="FOREIGN_MANUFACTURER"
    )
    response = cert_service.generate_roadmap(request)
    assert response.applicable_scheme in ("SCHEME_I_FMCS", "SCHEME_IV_FMCS")
    assert response.requires_air is True
    assert any(doc.category == "AIR_FOREIGN" for doc in response.document_checklist)


def test_roadmap_capital_goods_scheme_x(cert_service):
    request = CertificationRoadmapRequest(
        product_name="Industrial Centrifugal Compressor",
        product_category="Industrial Machinery & Capital Goods"
    )
    response = cert_service.generate_roadmap(request)
    assert response.applicable_scheme == "SCHEME_X_CAPITAL_GOODS"


def test_roadmap_hallmarking_precious_metals(cert_service):
    request = CertificationRoadmapRequest(
        product_name="22K Gold Necklace",
        product_category="Precious Metals & Jewellery"
    )
    response = cert_service.generate_roadmap(request)
    assert response.applicable_scheme == "HALLMARKING"
    assert "HUID" in response.route_rationale or "Hallmarking" in response.route_rationale


def test_roadmap_eco_mark(cert_service):
    request = CertificationRoadmapRequest(
        product_name="Biodegradable Laundry Detergent",
        scheme_code="ECO_MARK"
    )
    response = cert_service.generate_roadmap(request)
    assert response.applicable_scheme == "ECO_MARK"
    assert "ECO Mark" in response.route_rationale or "पर्यावरण" in response.route_rationale or "சுற்றுச்சூழல்" in response.route_rationale


def test_roadmap_management_systems(cert_service):
    request = CertificationRoadmapRequest(
        product_name="ISO 9001 Quality Management System Certification",
        product_category="Management Systems"
    )
    response = cert_service.generate_roadmap(request)
    assert response.applicable_scheme == "SCHEME_IV_MSCS"


def test_roadmap_multilingual_hindi_and_tamil(cert_service):
    # Hindi
    req_hi = CertificationRoadmapRequest(
        product_name="Electric Ceiling Fan",
        standard_number="IS 17803:2022",
        language="hi"
    )
    res_hi = cert_service.generate_roadmap(req_hi)
    assert "बीआईएस प्रमाणन मार्ग" in res_hi.route_rationale
    assert "आधिकारिक अस्वीकरण" in res_hi.disclaimer

    # Tamil
    req_ta = CertificationRoadmapRequest(
        product_name="Electric Ceiling Fan",
        standard_number="IS 17803:2022",
        language="ta"
    )
    res_ta = cert_service.generate_roadmap(req_ta)
    assert "சான்றிதழ் வழி" in res_ta.route_rationale
    assert "அதிகாரப்பூர்வ மறுப்பு" in res_ta.disclaimer


def test_schemes_catalogue_completeness_and_fields():
    schemes = get_localized_all_schemes("en")
    assert len(schemes) == 10
    
    expected_codes = {
        "SCHEME_I_ISI_NORMAL",
        "SCHEME_I_ISI_SIMPLIFIED",
        "SCHEME_I_FMCS",
        "ECO_MARK",
        "SCHEME_II_CRS",
        "SCHEME_III_COC",
        "SCHEME_IV_MSCS",
        "SCHEME_X_CAPITAL_GOODS",
        "HALLMARKING",
        "LABORATORY_RECOGNITION"
    }
    actual_codes = {s["scheme_code"] for s in schemes}
    assert expected_codes == actual_codes

    for s in schemes:
        assert s["name"]
        assert s["classification"]
        assert s["manufacturer_scope"] in ("DOMESTIC", "FOREIGN", "DOMESTIC_AND_FOREIGN", "ORGANIZATIONS_AND_LABS")
        assert s["legal_act_and_regulation"]
        assert s["official_reference_url"].startswith("http")
        assert s["source_verification_date"] == "2026-10-10"
        assert s["data_confidence"] == "OFFICIAL_STATUTORY_VERIFIED"
        assert len(s["applicable_sectors"]) > 0
        assert len(s["required_documents_checklist"]) > 0
        assert s["application_procedure_summary"]
        assert s["fee_structure_summary"]


def test_schemes_catalogue_filtering():
    # Filter by manufacturer_scope DOMESTIC
    domestic_schemes = get_localized_all_schemes(manufacturer_scope="DOMESTIC")
    for s in domestic_schemes:
        assert s["manufacturer_scope"] in ("DOMESTIC", "DOMESTIC_AND_FOREIGN")
    
    # Filter by manufacturer_scope FOREIGN
    foreign_schemes = get_localized_all_schemes(manufacturer_scope="FOREIGN")
    for s in foreign_schemes:
        assert s["manufacturer_scope"] in ("FOREIGN", "DOMESTIC_AND_FOREIGN")

    # Search keyword
    crs_search = get_localized_all_schemes(search="Compulsory Registration")
    assert any(s["scheme_code"] == "SCHEME_II_CRS" for s in crs_search)

    # Unknown keyword safely returns empty list
    unknown_search = get_localized_all_schemes(search="NonExistentSchemeXYZ999")
    assert len(unknown_search) == 0


def test_schemes_legacy_alias_resolution(cert_service):
    # Test that querying by legacy alias SCHEME_I_ISI resolves cleanly
    req_legacy_isi = CertificationRoadmapRequest(scheme_code="SCHEME_I_ISI")
    res_isi = cert_service.generate_roadmap(req_legacy_isi)
    assert res_isi.applicable_scheme in ("SCHEME_I_ISI_NORMAL", "SCHEME_I_ISI")

    # Test legacy alias SCHEME_IV_FMCS
    req_legacy_fmcs = CertificationRoadmapRequest(scheme_code="SCHEME_IV_FMCS")
    res_fmcs = cert_service.generate_roadmap(req_legacy_fmcs)
    assert res_fmcs.applicable_scheme in ("SCHEME_I_FMCS", "SCHEME_IV_FMCS")
    assert res_fmcs.requires_air is True


def test_mandatory_qco_flag_integrity_and_disclaimer(cert_service):
    """Verify that voluntary standards do not assume mandatory QCO without evidence."""
    req_voluntary = CertificationRoadmapRequest(standard_number="IS 456:2000")
    res = cert_service.generate_roadmap(req_voluntary)
    assert res.is_mandatory_qco is False
    assert "does not constitute official BIS approval" in res.disclaimer


def test_ambiguous_request_guidance_fallback(cert_service):
    """Verify handling when neither product name nor standard is specified."""
    req_blank = CertificationRoadmapRequest()
    res = cert_service.generate_roadmap(req_blank)
    assert res.applicable_scheme is not None
    assert len(res.steps) >= 4
    assert res.disclaimer is not None


def test_official_portal_links_present_in_roadmap(cert_service):
    """Verify all roadmap responses provide verified .gov.in official portal links."""
    req = CertificationRoadmapRequest(product_name="Mobile Phone Charger", standard_number="IS 13252")
    res = cert_service.generate_roadmap(req)
    assert len(res.official_sources) > 0
    assert all("bis.gov.in" in src.url or "manakonline.in" in src.url or "crsbis.in" in src.url for src in res.official_sources)



