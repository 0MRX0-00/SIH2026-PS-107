import logging
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Depends, Query, Path, status
from app.schemas.intelligence import (
    LaboratorySearchRequest,
    LaboratorySearchResponse,
    LaboratoryItem,
    LaboratoryStatsResponse
)
from app.services.laboratory_service import LaboratoryService
from app.api.v1.endpoints.admin import verify_admin_key

logger = logging.getLogger("ebis_sahayak.laboratories_api")
router = APIRouter()


def get_laboratory_service() -> LaboratoryService:
    return LaboratoryService()


@router.get("/stats", response_model=LaboratoryStatsResponse)
def get_laboratory_stats(
    service: LaboratoryService = Depends(get_laboratory_service)
):
    """
    Get directory statistics including total verified laboratories, category counts, and states.
    """
    try:
        return service.get_stats()
    except Exception as e:
        logger.exception(f"Laboratory stats error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve laboratory statistics."
        )


@router.post("/search", response_model=LaboratorySearchResponse)
def search_laboratories(
    request: LaboratorySearchRequest,
    service: LaboratoryService = Depends(get_laboratory_service)
):
    """
    Search and filter verified BIS-recognized and NABL-accredited testing laboratories.
    Supports search query, state, district, standard number, recognition type, status, and server-side pagination.
    """
    try:
        return service.search_laboratories(request)
    except Exception as e:
        logger.exception(f"Laboratory search error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to search laboratory directory. Please refine your search criteria."
        )


@router.get("/", response_model=LaboratorySearchResponse)
def list_laboratories(
    query: Optional[str] = Query(None, description="Free text keyword or capability search"),
    lab_code: Optional[str] = Query(None, description="Filter by official lab code"),
    city: Optional[str] = Query(None, description="Filter by city"),
    district: Optional[str] = Query(None, description="Filter by district"),
    state: Optional[str] = Query(None, description="Filter by state"),
    standard_number: Optional[str] = Query(None, description="Filter by accredited standard number"),
    recognition_type: Optional[str] = Query(None, description="BIS_RECOGNIZED, BIS_EMPANELLED, BIS_CENTRAL, BIS_BRANCH, NABL_ACCREDITED"),
    status: Optional[str] = Query(None, description="ACTIVE, EXPIRED, SUSPENDED"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    sort_by: Optional[str] = Query("name", description="Sort field: name, code, state, city, validity"),
    sort_order: Optional[str] = Query("asc", description="Sort order: asc, desc"),
    language: Optional[str] = Query("en", description="Target language: en, hi, ta"),
    service: LaboratoryService = Depends(get_laboratory_service)
):
    """
    Paginated list of verified laboratories with multi-criteria filtering.
    """
    req = LaboratorySearchRequest(
        query=query,
        lab_code=lab_code,
        city=city,
        district=district,
        state=state,
        standard_number=standard_number,
        recognition_type=recognition_type,
        status=status,
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        sort_order=sort_order,
        language=language or "en"
    )
    return service.search_laboratories(req)


@router.get("/{id_or_code}", response_model=LaboratoryItem)
def get_laboratory_details(
    id_or_code: str = Path(..., description="Laboratory unique ID or official Lab Code"),
    language: Optional[str] = Query("en", description="Target language: en, hi, ta"),
    service: LaboratoryService = Depends(get_laboratory_service)
):
    """
    Retrieve single laboratory details by ID or official Lab Code.
    """
    lab = service.get_by_id_or_code(id_or_code, language=language or "en")
    if not lab:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Laboratory '{id_or_code}' not found in official verified directory."
        )
    return lab


@router.post("/admin/refresh", response_model=Dict[str, Any])
def refresh_laboratory_directory(
    service: LaboratoryService = Depends(get_laboratory_service),
    _admin_authenticated: bool = Depends(verify_admin_key)
):
    """
    Admin operation: Refresh laboratory records from official BIS LIMS sources.
    Requires administrator authentication via X-Admin-Key header.
    """
    try:
        return service.refresh_from_source()
    except Exception as e:
        logger.exception("Laboratory refresh error occurred on server")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to refresh laboratory directory due to an internal server error. Please check server logs."
        )
