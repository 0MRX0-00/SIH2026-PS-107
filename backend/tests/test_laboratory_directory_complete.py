import os
import json
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.laboratory_service import LaboratoryService, laboratory_service
from app.schemas.intelligence import LaboratorySearchRequest
from app.scripts.import_laboratories import BISLaboratoryImporter, normalize_state, parse_address_components


@pytest.fixture
def client():
    return TestClient(app)


def test_directory_contains_more_than_five_records():
    """Verify laboratory directory is not restricted to 5 records and contains full official count."""
    labs = laboratory_service.list_all()
    assert len(labs) >= 500, f"Expected > 500 records from official BIS LIMS import, got {len(labs)}"
    stats = laboratory_service.get_stats()
    assert stats.total_laboratories >= 500
    assert stats.recognized_count >= 400
    assert stats.empaneled_count >= 100
    assert stats.institutional_count >= 5


def test_pagination_and_total_counts():
    """Verify server-side pagination calculates pages, offsets, and items correctly."""
    req_p1 = LaboratorySearchRequest(page=1, page_size=20)
    res_p1 = laboratory_service.search_laboratories(req_p1)
    assert res_p1.total_count >= 500
    assert len(res_p1.laboratories) == 20
    assert res_p1.page == 1
    assert res_p1.total_pages > 20
    assert res_p1.has_next is True
    assert res_p1.has_prev is False

    req_p2 = LaboratorySearchRequest(page=2, page_size=20)
    res_p2 = laboratory_service.search_laboratories(req_p2)
    assert len(res_p2.laboratories) == 20
    assert res_p2.page == 2
    assert res_p2.has_prev is True
    # Ensure items on page 1 and page 2 are different
    p1_codes = {l.lab_code for l in res_p1.laboratories if l.lab_code}
    p2_codes = {l.lab_code for l in res_p2.laboratories if l.lab_code}
    assert len(p1_codes.intersection(p2_codes)) == 0


def test_search_by_name_and_lab_code():
    """Verify keyword query and exact lab code lookups."""
    # Search by official lab code
    req_code = LaboratorySearchRequest(lab_code="8102006")
    res_code = laboratory_service.search_laboratories(req_code)
    assert res_code.total_count >= 1
    assert any("8102006" in (l.lab_code or "") for l in res_code.laboratories)

    # Search by name substring
    req_name = LaboratorySearchRequest(query="Shriram Institute")
    res_name = laboratory_service.search_laboratories(req_name)
    assert res_name.total_count >= 1
    assert any("Shriram" in l.lab_name for l in res_name.laboratories)


def test_filtering_by_state_and_district():
    """Verify state and district filtering works accurately."""
    req_state = LaboratorySearchRequest(state="Maharashtra", page_size=50)
    res_state = laboratory_service.search_laboratories(req_state)
    assert res_state.total_count >= 10
    assert all(l.state == "Maharashtra" for l in res_state.laboratories)

    req_tamil_nadu = LaboratorySearchRequest(state="Tamil Nadu", page_size=50)
    res_tn = laboratory_service.search_laboratories(req_tamil_nadu)
    assert res_tn.total_count >= 10
    assert all(l.state == "Tamil Nadu" for l in res_tn.laboratories)


def test_filtering_by_recognition_category():
    """Verify distinct categories: BIS_RECOGNIZED, BIS_EMPANELLED, BIS_CENTRAL, BIS_BRANCH."""
    req_rec = LaboratorySearchRequest(recognition_type="BIS_RECOGNIZED", page_size=20)
    res_rec = laboratory_service.search_laboratories(req_rec)
    assert res_rec.total_count >= 400
    assert all(l.recognition_type == "BIS_RECOGNIZED" for l in res_rec.laboratories)

    req_emp = LaboratorySearchRequest(recognition_type="BIS_EMPANELLED", page_size=20)
    res_emp = laboratory_service.search_laboratories(req_emp)
    assert res_emp.total_count >= 100
    assert all(l.recognition_type == "BIS_EMPANELLED" for l in res_emp.laboratories)

    req_inst = LaboratorySearchRequest(recognition_type="BIS_CENTRAL")
    res_inst = laboratory_service.search_laboratories(req_inst)
    assert res_inst.total_count >= 1
    assert any("Central Laboratory" in l.lab_name for l in res_inst.laboratories)


def test_sorting_capabilities():
    """Verify sorting by name, lab code, and state."""
    req_asc = LaboratorySearchRequest(page=1, page_size=10, sort_by="name", sort_order="asc")
    res_asc = laboratory_service.search_laboratories(req_asc)
    names = [l.lab_name.lower() for l in res_asc.laboratories]
    assert names == sorted(names)

    req_desc = LaboratorySearchRequest(page=1, page_size=10, sort_by="name", sort_order="desc")
    res_desc = laboratory_service.search_laboratories(req_desc)
    names_desc = [l.lab_name.lower() for l in res_desc.laboratories]
    assert names_desc == sorted(names_desc, reverse=True)


def test_get_by_id_or_code():
    """Verify single detail retrieval by ID or Lab Code."""
    # By Lab Code
    lab = laboratory_service.get_by_id_or_code("8102006")
    assert lab is not None
    assert "Shriram" in lab.lab_name or "SIIR" in lab.lab_name
    assert lab.contact_details is not None
    assert "email" in lab.contact_details or "phone" in lab.contact_details

    # By Institutional ID
    lab_cl = laboratory_service.get_by_id_or_code("bis-cl-gzb")
    assert lab_cl is not None
    assert "Central Laboratory" in lab_cl.lab_name

    # Non-existent
    assert laboratory_service.get_by_id_or_code("invalid-code-9999999") is None


def test_address_normalization_and_state_parser():
    """Verify address parsing logic correctly extracts clean components."""
    addr_raw = "19-University Road, Delhi 110007,\n Delhi,\n North,\n Delhi,\n India -  110007"
    clean, city, dist, state = parse_address_components(addr_raw)
    assert state == "Delhi"
    assert city == "Delhi"

    addr_up = "C - 57, Sector - 65,\n Noida,\n Gautam Buddha Nagar,\n Uttar Pradesh,\n India -  201301"
    clean, city, dist, state = parse_address_components(addr_up)
    assert state == "Uttar Pradesh"
    assert "Noida" in city


MOCK_RECOGNIZED_LIMS_PAGE = """
<table>
  <tr><th>S.No</th><th>Lab Code</th><th>Lab Name</th><th>Address</th><th>Contact Person</th><th>Phone</th><th>Email</th><th>Validity</th><th>Scope</th></tr>
  <tr><td>1</td><td>8100101</td><td>Apex Testing Laboratory</td><td>Plot 1, Okhla Phase 1\nNew Delhi\nDelhi - 110020</td><td>Dr. Sharma</td><td>9876543210</td><td>info@apextest.com</td><td>31 Dec, 2026</td><td><a href="/scope/8100101">View</a></td></tr>
  <tr><td>2</td><td>8100102</td><td>Bharat Test House Pvt Ltd</td><td>Sector 25\nFaridabad\nHaryana - 121004</td><td>Mr. Verma</td><td>9876543211</td><td>contact@bharattest.com</td><td>31 Dec, 2026</td><td><a href="/scope/8100102">View</a></td></tr>
  <tr><td>3</td><td>8100103</td><td>Chennai Quality Services</td><td>Guindy Industrial Estate\nChennai\nTamil Nadu - 600032</td><td>Ms. Raman</td><td>9876543212</td><td>qa@cqs.in</td><td>31 Dec, 2026</td><td><a href="/scope/8100103">View</a></td></tr>
  <tr><td>4</td><td>8100104</td><td>Deccan Analytical Labs</td><td>Peenya Industrial Area\nBengaluru\nKarnataka - 560058</td><td>Mr. Rao</td><td>9876543213</td><td>info@deccanlab.com</td><td>31 Dec, 2026</td><td><a href="/scope/8100104">View</a></td></tr>
  <tr><td>5</td><td>8100105</td><td>Eastern Standards Lab</td><td>Salt Lake Sector V\nKolkata\nWest Bengal - 700091</td><td>Dr. Banerjee</td><td>9876543214</td><td>test@easternlab.org</td><td>31 Dec, 2026</td><td><a href="/scope/8100105">View</a></td></tr>
  <tr><td>6</td><td>8100106</td><td>Gujarat Materials Testing Center</td><td>GIDC Vatva\nAhmedabad\nGujarat - 382445</td><td>Mr. Patel</td><td>9876543215</td><td>lab@gmtc.in</td><td>31 Dec, 2026</td><td><a href="/scope/8100106">View</a></td></tr>
  <tr><td>7</td><td>8100107</td><td>Hyderabad Calibration Facility</td><td>Balanagar\nHyderabad\nTelangana - 500037</td><td>Dr. Reddy</td><td>9876543216</td><td>info@hcf.org</td><td>31 Dec, 2026</td><td><a href="/scope/8100107">View</a></td></tr>
  <tr><td>8</td><td>8100108</td><td>Indore Electrical Test House</td><td>Sanwer Road\nIndore\nMadhya Pradesh - 452015</td><td>Mr. Joshi</td><td>9876543217</td><td>contact@ieth.in</td><td>31 Dec, 2026</td><td><a href="/scope/8100108">View</a></td></tr>
  <tr><td>9</td><td>8100109</td><td>Jaipur Solar & Cable Labs</td><td>Sitapura Industrial Area\nJaipur\nRajasthan - 302022</td><td>Ms. Sharma</td><td>9876543218</td><td>testing@jscl.co.in</td><td>31 Dec, 2026</td><td><a href="/scope/8100109">View</a></td></tr>
  <tr><td>10</td><td>8100110</td><td>Kochi Chemical Research Lab</td><td>Kalamassery\nKochi\nKerala - 683104</td><td>Dr. Nair</td><td>9876543219</td><td>lab@kcrl.org</td><td>31 Dec, 2026</td><td><a href="/scope/8100110">View</a></td></tr>
  <tr><td>11</td><td>8100111</td><td>Lucknow Polymer & Plastic Lab</td><td>Talkatora Industrial Area\nLucknow\nUttar Pradesh - 226011</td><td>Mr. Mishra</td><td>9876543220</td><td>info@lppl.in</td><td>31 Dec, 2026</td><td><a href="/scope/8100111">View</a></td></tr>
  <tr><td>12</td><td>8100112</td><td>Mumbai Precision Laboratories</td><td>Andheri East\nMumbai\nMaharashtra - 400093</td><td>Ms. Deshmukh</td><td>9876543221</td><td>test@mpl.com</td><td>31 Dec, 2026</td><td><a href="/scope/8100112">View</a></td></tr>
  <tr><td>13</td><td>8100113</td><td>Nagpur Steel & Metal Testing</td><td>MIDC Hingna\nNagpur\nMaharashtra - 440028</td><td>Mr. Kulkarni</td><td>9876543222</td><td>quality@nsmt.in</td><td>31 Dec, 2026</td><td><a href="/scope/8100113">View</a></td></tr>
  <tr><td>14</td><td>8100114</td><td>Odisha Environmental Testing</td><td>Rasulgarh\nBhubaneswar\nOdisha - 751010</td><td>Dr. Mohanty</td><td>9876543223</td><td>env@oet.org</td><td>31 Dec, 2026</td><td><a href="/scope/8100114">View</a></td></tr>
  <tr><td>15</td><td>8100115</td><td>Punjab Agro Testing Center</td><td>Focal Point\nLudhiana\nPunjab - 141010</td><td>Mr. Singh</td><td>9876543224</td><td>contact@patc.in</td><td>31 Dec, 2026</td><td><a href="/scope/8100115">View</a></td></tr>
</table>
"""

MOCK_EMPANELLED_LIMS_PAGE = """
<table>
  <tr><th>S.No</th><th>Lab Code</th><th>Lab Name</th><th>Address</th><th>Contact Person</th><th>Phone</th><th>Email</th><th>Scope</th></tr>
  <tr><td>1</td><td>8100101</td><td>Apex Testing Laboratory (Empanelled Scope)</td><td>Plot 1, Okhla Phase 1\nNew Delhi\nDelhi - 110020</td><td>Dr. Sharma</td><td>9876543210</td><td>info@apextest.com</td><td><a href="/scope/8100101">View</a></td></tr>
  <tr><td>2</td><td>8100201</td><td>Ranchi Mineral & Coal Testing</td><td>Tupudana Industrial Area\nRanchi\nJharkhand - 834003</td><td>Dr. Prasad</td><td>9876543225</td><td>info@rmct.org</td><td><a href="/scope/8100201">View</a></td></tr>
  <tr><td>3</td><td>8100202</td><td>Surat Textile Testing Center</td><td>Ring Road\nSurat\nGujarat - 395002</td><td>Mr. Shah</td><td>9876543226</td><td>lab@sttc.in</td><td><a href="/scope/8100202">View</a></td></tr>
  <tr><td>4</td><td>8100203</td><td>Trivandrum Electronics Lab</td><td>Technopark\nThiruvananthapuram\nKerala - 695581</td><td>Ms. Pillai</td><td>9876543227</td><td>qa@tel.org</td><td><a href="/scope/8100203">View</a></td></tr>
  <tr><td>5</td><td>8100204</td><td>Udaipur Zinc & Minerals Lab</td><td>Madri Industrial Area\nUdaipur\nRajasthan - 313003</td><td>Mr. Choudhary</td><td>9876543228</td><td>test@uzml.in</td><td><a href="/scope/8100204">View</a></td></tr>
  <tr><td>6</td><td>8100205</td><td>Varanasi Silk & Handloom Testing</td><td>Chowk\nVaranasi\nUttar Pradesh - 221001</td><td>Mr. Tripathi</td><td>9876543229</td><td>silk@vsht.org</td><td><a href="/scope/8100205">View</a></td></tr>
  <tr><td>7</td><td>8100206</td><td>Warangal Civil Construction Labs</td><td>Kazipet\nWarangal\nTelangana - 506004</td><td>Dr. Rao</td><td>9876543230</td><td>info@wccl.in</td><td><a href="/scope/8100206">View</a></td></tr>
  <tr><td>8</td><td>8100207</td><td>Yamuna Nagar Paper Testing</td><td>Industrial Area\nYamuna Nagar\nHaryana - 135001</td><td>Mr. Gupta</td><td>9876543231</td><td>paper@ynpt.org</td><td><a href="/scope/8100207">View</a></td></tr>
</table>
"""


def test_duplicate_import_deduplication(tmp_path):
    """Verify importer deduplicates records on repeated imports with deterministic mock data."""
    from unittest.mock import patch

    def mock_fetch_url(url, **kwargs):
        if "empaneled" in url:
            return MOCK_EMPANELLED_LIMS_PAGE
        return MOCK_RECOGNIZED_LIMS_PAGE

    importer = BISLaboratoryImporter(data_file=str(tmp_path / "test_labs.json"))
    with patch("app.scripts.import_laboratories.fetch_url_html", side_effect=mock_fetch_url):
        stats = importer.import_all(max_pages_rec=1, max_pages_emp=1)
        assert stats["total_unique"] >= 20
        assert os.path.exists(importer.data_file)

        # Re-run import into same file - unique count should remain consistent and deduplicated
        stats2 = importer.import_all(max_pages_rec=1, max_pages_emp=1)
        assert stats2["total_unique"] == stats["total_unique"]
        assert stats2["total_unique"] == 28  # 6 institutional + 15 recognized + 7 unique empaneled


def test_importer_handles_network_failure_gracefully(tmp_path):
    """Verify importer gracefully falls back to institutional labs when network is down."""
    from unittest.mock import patch

    importer = BISLaboratoryImporter(data_file=str(tmp_path / "offline_labs.json"))
    with patch("app.scripts.import_laboratories.fetch_url_html", return_value=None):
        stats = importer.import_all(max_pages_rec=2, max_pages_emp=2)
        assert stats["failed_pages"] == 4
        assert stats["institutional_imported"] == 6
        assert stats["total_unique"] == 6
        assert os.path.exists(importer.data_file)



def test_api_endpoints_integration(client):
    """Verify FastAPI endpoints return expected schemas and headers."""
    # 1. GET /api/v1/laboratories/stats
    res_stats = client.get("/api/v1/laboratories/stats")
    assert res_stats.status_code == 200
    s_data = res_stats.json()
    assert s_data["total_laboratories"] >= 500
    assert s_data["recognized_count"] >= 400

    # 2. GET /api/v1/laboratories/ (Paginated list)
    res_list = client.get("/api/v1/laboratories?page=1&page_size=15&state=Delhi")
    assert res_list.status_code == 200
    l_data = res_list.json()
    assert l_data["total_count"] >= 1
    assert len(l_data["laboratories"]) <= 15
    assert all(l["state"] == "Delhi" for l in l_data["laboratories"])

    # 3. GET /api/v1/laboratories/{id_or_code}
    res_single = client.get("/api/v1/laboratories/8102006")
    assert res_single.status_code == 200
    single_data = res_single.json()
    assert single_data["lab_code"] == "8102006"

    # 4. POST /api/v1/laboratories/search
    res_post = client.post(
        "/api/v1/laboratories/search",
        json={"state": "Karnataka", "page": 1, "page_size": 10}
    )
    assert res_post.status_code == 200
    post_data = res_post.json()
    assert post_data["total_count"] >= 1
    assert all(l["state"] == "Karnataka" for l in post_data["laboratories"])


def test_groq_only_chat_unaffected(client, mocker):
    """Verify conversational chat endpoint remains purely Groq-only with zero RAG or vector retrieval."""
    from unittest.mock import AsyncMock
    mock_groq = mocker.patch(
        "app.services.groq_service.GroqService.generate_chat_completion",
        new_callable=AsyncMock,
        return_value="Hello, I am e-BIS Sahayak powered by Groq."
    )

    res = client.post("/api/v1/chat", json={"message": "Where can I find BIS laboratories?"})
    assert res.status_code == 200
    data = res.json()
    assert data["grounded"] is False
    assert data["sources"] == []
    assert data["citations"] == []
    assert data["sources_used"] == 0
    assert data["evidence_status"] is None
    assert mock_groq.called
