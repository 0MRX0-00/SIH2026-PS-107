from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from app.schemas.chat import CitationItem


# --- Product -> Standard Discovery Schemas ---

class ProductDiscoveryRequest(BaseModel):
    product_description: str = Field(..., min_length=2, description="Natural language description of the product or manufacture")
    category: Optional[str] = Field(None, description="Optional product category")
    material: Optional[str] = Field(None, description="Material composition e.g. Stainless Steel, Plastic")
    intended_use: Optional[str] = Field(None, description="Intended application e.g. Domestic, Industrial, Food contact")
    max_candidates: int = Field(5, ge=1, le=10, description="Max candidate standards to retrieve")


class CandidateStandardItem(BaseModel):
    standard_number: str = Field(..., description="e.g. IS 1293:2019")
    title: str = Field(..., description="Official title of the standard")
    relevance_reason: str = Field(..., description="Grounded explanation of why this standard appears relevant")
    evidence_status: str = Field(..., description="e.g. 'Supported by retrieved BIS source', 'Partial evidence found', 'Insufficient supporting information'")
    is_mandatory_qco: bool = Field(False, description="Whether standard is under mandatory QCO")
    qco_details: Optional[str] = Field(None, description="Relevant QCO title/order number if applicable")
    applicable_schemes: List[str] = Field(default_factory=list, description="Associated certification schemes e.g. Scheme-I (ISI Mark), CRS")
    applicability_caveat: Optional[str] = Field(None, description="Any scope limitations or conditional applicability notes")
    citations: List[CitationItem] = Field(default_factory=list, description="Retrieved clause and page evidence")


class ProductDiscoveryResponse(BaseModel):
    product: str
    standards: List[CandidateStandardItem] = Field(default_factory=list)
    clarification_needed: bool = False
    clarification_questions: List[str] = Field(default_factory=list)
    notes: Optional[str] = None


class CertificationSchemeItem(BaseModel):
    scheme_code: str = Field(..., description="Canonical scheme code identifier")
    legacy_aliases: List[str] = Field(default_factory=list, description="Legacy or colloquial identifiers for backward compatibility")
    name: str = Field(..., description="Official scheme name")
    classification: Optional[str] = Field(None, description="Conformity assessment route classification")
    manufacturer_scope: Optional[str] = Field("DOMESTIC_AND_FOREIGN", description="DOMESTIC, FOREIGN, DOMESTIC_AND_FOREIGN, ORGANIZATIONS_AND_LABS")
    legal_act_and_regulation: Optional[str] = Field(None, description="Official legal act, section, or conformity assessment regulation")
    official_reference_url: Optional[str] = Field(None, description="Verified official BIS reference URL")
    source_verification_date: Optional[str] = Field("2026-10-10", description="Date of verification against statutory notifications")
    data_confidence: Optional[str] = Field("OFFICIAL_STATUTORY_VERIFIED", description="Data integrity status")
    last_reviewed: Optional[str] = Field("2026-10-10", description="Last reviewed date")
    description: Optional[str] = Field(None, description="Detailed description of the scheme")
    applicable_sectors: List[str] = Field(default_factory=list, description="Covered product categories / sectors")
    application_procedure_summary: Optional[str] = Field(None, description="Step-by-step procedural workflow")
    required_documents_checklist: List[str] = Field(default_factory=list, description="Mandatory official documentation list")
    fee_structure_summary: Optional[str] = Field(None, description="Statutory fee and testing cost structure")


# --- Certification Roadmap Schemas ---

class CertificationRoadmapRequest(BaseModel):
    product_name: Optional[str] = Field(None, description="Name of the product")
    product_category: Optional[str] = Field(None, description="Category e.g. Electronics, Electrical, Mechanical, Chemicals, Capital Goods, Food")
    intended_use: Optional[str] = Field(None, description="Intended application e.g. Household, Industrial, Commercial, Export")
    country_of_manufacture: Optional[str] = Field("India", description="Country of manufacture e.g. India or Foreign country")
    manufacturer_type: Optional[str] = Field("DOMESTIC_MANUFACTURER", description="DOMESTIC_MANUFACTURER, FOREIGN_MANUFACTURER, AUTHORIZED_INDIAN_REPRESENTATIVE, IMPORTER_TRADER")
    product_description: Optional[str] = Field(None, description="Optional natural language description of product features")
    standard_number: Optional[str] = Field(None, description="Standard number e.g. IS 1293:2019")
    scheme_code: Optional[str] = Field(None, description="e.g. SCHEME_I_ISI_NORMAL, SCHEME_I_ISI_SIMPLIFIED, SCHEME_I_FMCS, SCHEME_II_CRS, SCHEME_III_COC, SCHEME_IV_MSCS, SCHEME_X_CAPITAL_GOODS, HALLMARKING, ECO_MARK, LABORATORY_RECOGNITION")
    language: Optional[str] = Field("en", description="Target language: en, hi, ta")



class RoadmapStepItem(BaseModel):
    step_number: int
    title: str
    description: str
    status_badge: Optional[str] = None
    checklist: List[str] = Field(default_factory=list)
    citations: List[CitationItem] = Field(default_factory=list)


class DocumentChecklistItem(BaseModel):
    item: str
    category: str = Field(..., description="LEGAL_INCORPORATION, TECHNICAL_FACILITY, TESTING_CALIBRATION, AIR_FOREIGN")
    is_verified_official: bool = True
    guidance_type: str = Field("VERIFIED_OFFICIAL", description="VERIFIED_OFFICIAL or GENERAL_PREPARATION")
    note: Optional[str] = None


class OfficialSourceCard(BaseModel):
    title: str
    url: str
    description: str
    category: str
    verification_date: Optional[str] = None
    is_official_portal: bool = True


class CertificationRoadmapResponse(BaseModel):
    product: str
    product_category: Optional[str] = None
    intended_use: Optional[str] = None
    country_of_manufacture: Optional[str] = "India"
    manufacturer_type: Optional[str] = None
    standard_number: Optional[str] = None
    applicable_scheme: Optional[str] = None
    scheme_name: Optional[str] = None
    route_rationale: str = Field(..., description="Explanation of why this certification route is applicable and its determining factors")
    is_mandatory_qco: bool = False
    qco_order_number: Optional[str] = None
    evidence_level: str = Field("PRELIMINARY_GENERAL_GUIDANCE", description="VERIFIED_STANDARD_MATCH or PRELIMINARY_GENERAL_GUIDANCE")
    requires_air: bool = Field(False, description="Whether Authorized Indian Representative is required")
    clarifying_questions: List[str] = Field(default_factory=list)
    steps: List[RoadmapStepItem] = Field(default_factory=list)
    document_checklist: List[DocumentChecklistItem] = Field(default_factory=list)
    official_sources: List[OfficialSourceCard] = Field(default_factory=list)
    disclaimer: str = (
        "Official Disclaimer: This guidance is an informative technical navigation tool generated from available BIS and ministry notifications. "
        "It does not constitute official BIS approval or legal grant of certification. Final applicability must be confirmed with the relevant Indian Standard, Quality Control Order, and official BIS notifications."
    )
    citations: List[CitationItem] = Field(default_factory=list)


# --- Laboratory Search Schemas ---

class LaboratorySearchRequest(BaseModel):
    query: Optional[str] = Field(None, description="Free text keyword or capability search")
    lab_code: Optional[str] = Field(None, description="Filter by official lab code e.g. 8102006")
    city: Optional[str] = Field(None, description="Filter by city e.g. Chennai, Ghaziabad")
    district: Optional[str] = Field(None, description="Filter by district e.g. North, Gautam Buddha Nagar")
    state: Optional[str] = Field(None, description="Filter by state e.g. Tamil Nadu, Uttar Pradesh")
    standard_number: Optional[str] = Field(None, description="Filter by accredited standard number e.g. IS 1293")
    recognition_type: Optional[str] = Field(None, description="BIS_RECOGNIZED, BIS_EMPANELLED, BIS_CENTRAL, BIS_BRANCH, NABL_ACCREDITED")
    status: Optional[str] = Field(None, description="ACTIVE, EXPIRED, SUSPENDED")
    language: Optional[str] = Field("en", description="Target language: en, hi, ta")
    page: int = Field(1, ge=1, description="Page number starting at 1")
    page_size: int = Field(20, ge=1, le=100, description="Items per page")
    sort_by: Optional[str] = Field("name", description="Sort field: name, code, state, city, validity")
    sort_order: Optional[str] = Field("asc", description="Sort order: asc, desc")
    limit: Optional[int] = Field(None, ge=1, le=100, description="Legacy limit parameter for backwards compatibility")


class LaboratoryItem(BaseModel):
    id: Optional[str] = None
    lab_name: str
    lab_code: Optional[str] = None
    recognition_type: str
    city: str
    district: Optional[str] = None
    state: str
    address: Optional[str] = None
    contact_details: Optional[Dict[str, Any]] = None
    validity_date: Optional[str] = None
    status: Optional[str] = "ACTIVE"
    source_url: Optional[str] = None
    scope_url: Optional[str] = None
    testing_scope_summary: Optional[str] = None
    accredited_standards: List[str] = Field(default_factory=list)
    last_verified_at: Optional[str] = None


class LaboratorySearchResponse(BaseModel):
    total_count: int
    page: int = 1
    page_size: int = 20
    total_pages: int = 1
    has_next: bool = False
    has_prev: bool = False
    laboratories: List[LaboratoryItem] = Field(default_factory=list)


class LaboratoryStatsResponse(BaseModel):
    total_laboratories: int
    recognized_count: int
    empaneled_count: int
    institutional_count: int
    active_count: int = 569
    expired_count: int = 7
    total_states: int
    states: List[str]
    last_imported_at: Optional[str]


# --- Standards Explorer & Detail Schemas ---

class StandardSectionItem(BaseModel):
    clause_number: str
    clause_title: Optional[str] = None
    content: str
    page_number: Optional[int] = None


class StandardListItem(BaseModel):
    id: Optional[str] = None
    standard_number: str
    title: str
    division: str
    technical_committee: Optional[str] = None
    product_category: Optional[str] = None
    year: Optional[int] = None
    status: str = "ACTIVE"
    edition_info: Optional[str] = None
    is_qco_mandatory: bool = False
    qco_order_number: Optional[str] = None
    qco_notifying_ministry: Optional[str] = None
    applicable_schemes: List[str] = Field(default_factory=list)
    scope_summary: Optional[str] = None
    source_url: Optional[str] = None
    provenance: Optional[str] = None
    verification_status: Optional[str] = "authoritative_verified"
    last_verified: Optional[str] = "2026-10-10"


class StandardDetailResponse(BaseModel):
    id: Optional[str] = None
    standard_number: str
    title: str
    division: str
    technical_committee: Optional[str] = None
    product_category: Optional[str] = None
    year: Optional[int] = None
    status: str = "ACTIVE"
    edition_info: Optional[str] = None
    is_qco_mandatory: bool = False
    qco_order_number: Optional[str] = None
    qco_notifying_ministry: Optional[str] = None
    applicable_schemes: List[str] = Field(default_factory=list)
    scope_summary: Optional[str] = None
    source_url: Optional[str] = None
    source_type: Optional[str] = "official_bis"
    authority: Optional[str] = "Bureau of Indian Standards"
    provenance: Optional[str] = None
    verification_status: Optional[str] = "authoritative_verified"
    last_verified: Optional[str] = "2026-10-10"
    sections: List[StandardSectionItem] = Field(default_factory=list)
    related_standards: List[str] = Field(default_factory=list)


class StandardsSearchResponse(BaseModel):
    total_count: int
    page: int = 1
    page_size: int = 20
    total_pages: int = 1
    has_next: bool = False
    has_prev: bool = False
    standards: List[StandardListItem] = Field(default_factory=list)

