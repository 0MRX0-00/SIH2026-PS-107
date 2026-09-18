from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query
from app.schemas.intelligence import (
    LaboratorySearchRequest,
    LaboratorySearchResponse,
    LaboratoryItem
)
from app.services.laboratory_service import LaboratoryService

router = APIRouter()

def get_laboratory_service() -> LaboratoryService:
    return LaboratoryService()

@router.post("/search", response_model=LaboratorySearchResponse)
def search_laboratories(
    request: LaboratorySearchRequest,
    service: LaboratoryService = Depends(get_laboratory_service)
):
    """
    Search and filter verified BIS-recognized and NABL-accredited testing laboratories.
    """
    try:
        return service.search_laboratories(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Laboratory search failed: {str(e)}")

@router.get("/", response_model=List[LaboratoryItem])
def list_laboratories(
    language: Optional[str] = Query("en", description="Target language: en, hi, ta"),
    service: LaboratoryService = Depends(get_laboratory_service)
):
    """
    List all verified laboratories in the directory.
    """
    return service.list_all(language=language or "en")
