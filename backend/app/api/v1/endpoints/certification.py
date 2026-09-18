from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends, Query
from app.schemas.intelligence import CertificationRoadmapRequest, CertificationRoadmapResponse
from app.services.certification_navigator_service import CertificationNavigatorService
from app.db.seed_intelligence import get_localized_all_schemes

router = APIRouter()

def get_certification_service() -> CertificationNavigatorService:
    return CertificationNavigatorService()

@router.post("/roadmap", response_model=CertificationRoadmapResponse)
def generate_certification_roadmap(
    request: CertificationRoadmapRequest,
    service: CertificationNavigatorService = Depends(get_certification_service)
):
    """
    Generate a 5-step guided BIS certification roadmap for a product, standard, or scheme.
    """
    try:
        return service.generate_roadmap(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Roadmap generation failed: {str(e)}")

@router.get("/schemes", response_model=List[Dict[str, Any]])
def list_certification_schemes(
    language: Optional[str] = Query("en", description="Target language: en, hi, ta")
):
    """
    List verified BIS certification schemes (e.g. Scheme-I ISI Mark, Scheme-II CRS, FMCS).
    """
    return get_localized_all_schemes(language or "en")
