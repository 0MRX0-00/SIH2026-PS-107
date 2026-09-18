import uuid
from typing import List, Optional
from pydantic import BaseModel, ConfigDict


class StandardSectionBase(BaseModel):
    clause_number: str
    clause_title: Optional[str] = None
    content: str
    page_number: Optional[int] = None


class StandardSectionResponse(StandardSectionBase):
    id: uuid.UUID
    standard_id: uuid.UUID

    model_config = ConfigDict(from_attributes=True)


class StandardBase(BaseModel):
    standard_number: str
    title: str
    division: str
    year: Optional[int] = None
    status: str = "ACTIVE"
    is_qco_mandatory: bool = False
    qco_order_number: Optional[str] = None
    scope_summary: Optional[str] = None


class StandardResponse(StandardBase):
    id: uuid.UUID
    document_id: Optional[uuid.UUID] = None
    sections: List[StandardSectionResponse] = []

    model_config = ConfigDict(from_attributes=True)
