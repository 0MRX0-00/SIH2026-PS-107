from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, Depends
from app.schemas.intelligence import StandardListItem, StandardDetailResponse
from app.services.standards_service import StandardsService

router = APIRouter()

def get_standards_service() -> StandardsService:
    return StandardsService()

@router.get("/", response_model=List[StandardListItem])
def list_or_search_standards(
    q: Optional[str] = Query(None, description="Search keyword, standard number, or product"),
    division: Optional[str] = Query(None, description="Filter by division e.g. Electrotechnical"),
    qco_only: Optional[bool] = Query(None, description="Filter standards with mandatory QCO"),
    limit: int = Query(50, ge=1, le=100),
    language: Optional[str] = Query("en", description="Target language: en, hi, ta"),
    service: StandardsService = Depends(get_standards_service)
):
    """
    Search and explore Indian Standards repository by keyword, division, or QCO status.
    """
    return service.search_standards(query=q, division=division, qco_only=qco_only, limit=limit, language=language or "en")

@router.get("/{standard_id_or_number}", response_model=StandardDetailResponse)
def get_standard_details(
    standard_id_or_number: str,
    language: Optional[str] = Query("en", description="Target language: en, hi, ta"),
    service: StandardsService = Depends(get_standards_service)
):
    """
    Retrieve comprehensive details for an Indian Standard including clause hierarchy and QCO status.
    """
    standard = service.get_standard_details(standard_id_or_number, language=language or "en")
    if not standard:
        raise HTTPException(status_code=404, detail=f"Standard '{standard_id_or_number}' not found in knowledge base.")
    return standard
