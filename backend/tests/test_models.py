import uuid
from app.models.standard import Standard, StandardSection
from app.models.citation import Citation
from app.models.certification import CertificationScheme


def test_standard_model_instantiation():
    std = Standard(
        standard_number="IS 1293:2019",
        title="Plugs and Socket-Outlets for Related Voltages up to and Including 250 V",
        division="Electrotechnical",
        year=2019,
        status="ACTIVE",
        is_qco_mandatory=True
    )
    assert std.standard_number == "IS 1293:2019"
    assert std.is_qco_mandatory is True
    assert std.status == "ACTIVE"
    assert std.division == "Electrotechnical"


def test_citation_model_instantiation():
    msg_id = uuid.uuid4()
    citation = Citation(
        message_id=msg_id,
        standard_number="IS 1293:2019",
        clause_ref="Clause 8.1",
        page_number=12,
        confidence_score=0.95
    )
    assert citation.standard_number == "IS 1293:2019"
    assert citation.clause_ref == "Clause 8.1"
    assert citation.confidence_score == 0.95
