import logging
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends, Query, status
from fastapi.responses import HTMLResponse, Response
from app.schemas.intelligence import (
    CertificationRoadmapRequest,
    CertificationRoadmapResponse,
    DossierExportRequest,
    DossierExportResponse,
)
from app.services.certification_navigator_service import CertificationNavigatorService
from app.services.dossier_service import DossierService
from app.db.seed_intelligence import get_localized_all_schemes

logger = logging.getLogger("ebis_sahayak.certification_api")
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
        logger.exception(f"Roadmap generation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate certification roadmap. Please verify your query parameters."
        )


@router.get("/schemes", response_model=List[Dict[str, Any]])
def list_certification_schemes(
    language: Optional[str] = Query("en", description="Target language: en, hi, ta"),
    search: Optional[str] = Query(None, description="Optional search query by name, keyword, or standard"),
    manufacturer_scope: Optional[str] = Query(None, description="Filter by manufacturer scope: ALL, DOMESTIC, FOREIGN, ORGANIZATIONS_AND_LABS"),
    classification: Optional[str] = Query(None, description="Filter by route classification")
):
    """
    List verified BIS conformity assessment schemes and routes (e.g. Scheme-I Normal, Scheme-I Simplified, FMCS, Scheme-II CRS, Eco Mark, Scheme-III CoC, Scheme-IV MSCS, Scheme-X, Hallmarking, LRS).
    """
    return get_localized_all_schemes(
        language=language or "en",
        search=search,
        manufacturer_scope=manufacturer_scope,
        classification=classification
    )


@router.post("/export-dossier", response_model=DossierExportResponse)
def export_certification_dossier(request: DossierExportRequest):
    """
    Export a formal, audit-ready compliance dossier for MSMEs, startups, and manufacturers.
    Returns standalone printable/savable HTML with statutory sign-off tables, milestones, and metadata.
    """
    try:
        return DossierService.generate_dossier(request)
    except Exception as e:
        logger.exception(f"Dossier generation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate compliance dossier."
        )


@router.post("/download-dossier")
def download_certification_dossier(request: DossierExportRequest):
    """
    Directly download the compliance dossier as an offline attachment (.html).
    """
    try:
        response_data = DossierService.generate_dossier(request)
        headers = {
            "Content-Disposition": f'attachment; filename="{response_data.file_name}"',
            "Content-Type": "text/html; charset=utf-8",
            "X-Dossier-ID": response_data.dossier_id,
        }
        return Response(content=response_data.html_content, media_type="text/html", headers=headers)
    except Exception as e:
        logger.exception(f"Dossier download error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to download compliance dossier."
        )

