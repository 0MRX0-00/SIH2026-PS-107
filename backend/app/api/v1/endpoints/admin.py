from fastapi import APIRouter, Header, HTTPException, status
from typing import List, Optional
from app.core.config import settings
from app.schemas.admin import (
    AdminDocumentItem,
    AdminOverviewResponse,
    AdminReindexRequest,
    AdminReindexResponse,
    AdminSystemStatusResponse,
)
from app.schemas.feedback import FeedbackItem
from app.services.admin_service import AdminService
from app.services.feedback_service import FeedbackService

router = APIRouter()
admin_service = AdminService()
feedback_service = FeedbackService()


def verify_admin_key(x_admin_key: Optional[str] = Header(None)):
    """Verifies that the caller has administrative privileges."""
    if not settings.ADMIN_API_KEY:
        return True
    if x_admin_key != settings.ADMIN_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing X-Admin-Key header for administrator access."
        )
    return True


@router.get("/overview", response_model=AdminOverviewResponse, summary="Admin Dashboard Overview Stats")
async def get_admin_overview(x_admin_key: Optional[str] = Header(None)) -> AdminOverviewResponse:
    verify_admin_key(x_admin_key)
    return admin_service.get_overview_statistics()


@router.get("/documents", response_model=List[AdminDocumentItem], summary="List Ingested Knowledge Base Documents")
async def get_admin_documents(x_admin_key: Optional[str] = Header(None)) -> List[AdminDocumentItem]:
    verify_admin_key(x_admin_key)
    return admin_service.list_indexed_documents()


@router.post("/documents/reindex", response_model=AdminReindexResponse, summary="Trigger Document Reindexing")
async def trigger_reindex(
    req: AdminReindexRequest = AdminReindexRequest(force=True),
    x_admin_key: Optional[str] = Header(None),
) -> AdminReindexResponse:
    verify_admin_key(x_admin_key)
    return admin_service.reindex_all(force=req.force)


@router.get("/feedback", response_model=List[FeedbackItem], summary="Get User Feedback Submissions")
async def get_admin_feedback(
    limit: int = 50,
    x_admin_key: Optional[str] = Header(None),
) -> List[FeedbackItem]:
    verify_admin_key(x_admin_key)
    return feedback_service.get_all_feedback(limit=limit)


@router.get("/system-status", response_model=AdminSystemStatusResponse, summary="Real-Time System Diagnostics")
async def get_system_status(x_admin_key: Optional[str] = Header(None)) -> AdminSystemStatusResponse:
    verify_admin_key(x_admin_key)
    return admin_service.get_system_status()
