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


# --- Certification Roadmap Schemas ---

class CertificationRoadmapRequest(BaseModel):
    product_name: Optional[str] = Field(None, description="Name or description of the product")
    standard_number: Optional[str] = Field(None, description="Standard number e.g. IS 1293:2019")
    scheme_code: Optional[str] = Field(None, description="e.g. SCHEME_I_ISI, SCHEME_II_CRS, FMCS")
    language: Optional[str] = Field("en", description="Target language: en, hi, ta")


class RoadmapStepItem(BaseModel):
    step_number: int
    title: str
    description: str
    status_badge: Optional[str] = None
    checklist: List[str] = Field(default_factory=list)
    citations: List[CitationItem] = Field(default_factory=list)


class CertificationRoadmapResponse(BaseModel):
    product: str
    standard_number: Optional[str] = None
    applicable_scheme: Optional[str] = None
    scheme_name: Optional[str] = None
    is_mandatory_qco: bool = False
    qco_order_number: Optional[str] = None
    steps: List[RoadmapStepItem] = Field(default_factory=list)
    disclaimer: str = (
        "Notice: This roadmap is an informative navigation guide generated from available BIS documentation. "
        "It does not constitute official BIS approval, authorization, or legal certification."
    )
    citations: List[CitationItem] = Field(default_factory=list)


# --- Laboratory Search Schemas ---

class LaboratorySearchRequest(BaseModel):
    query: Optional[str] = Field(None, description="Free text keyword or capability search")
    city: Optional[str] = Field(None, description="Filter by city e.g. Chennai, Ghaziabad")
    state: Optional[str] = Field(None, description="Filter by state e.g. Tamil Nadu, Uttar Pradesh")
    standard_number: Optional[str] = Field(None, description="Filter by accredited standard number e.g. IS 1293")
    recognition_type: Optional[str] = Field(None, description="BIS_CENTRAL, BIS_BRANCH, NABL_ACCREDITED")
    language: Optional[str] = Field("en", description="Target language: en, hi, ta")
    limit: int = Field(20, ge=1, le=100)


class LaboratoryItem(BaseModel):
    id: Optional[str] = None
    lab_name: str
    lab_code: Optional[str] = None
    recognition_type: str
    city: str
    state: str
    address: Optional[str] = None
    contact_details: Optional[Dict[str, Any]] = None
    testing_scope_summary: Optional[str] = None
    accredited_standards: List[str] = Field(default_factory=list)


class LaboratorySearchResponse(BaseModel):
    total_count: int
    laboratories: List[LaboratoryItem] = Field(default_factory=list)


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
    year: Optional[int] = None
    status: str
    is_qco_mandatory: bool
    scope_summary: Optional[str] = None


class StandardDetailResponse(BaseModel):
    id: Optional[str] = None
    standard_number: str
    title: str
    division: str
    year: Optional[int] = None
    status: str
    is_qco_mandatory: bool
    qco_order_number: Optional[str] = None
    scope_summary: Optional[str] = None
    sections: List[StandardSectionItem] = Field(default_factory=list)
    related_standards: List[str] = Field(default_factory=list)
