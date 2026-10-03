from fastapi import APIRouter
from sqlalchemy import text
from app.core.config import settings
from app.db.session import AsyncSessionLocal
from app.schemas.health import DetailedHealthResponse, SubsystemStatus

router = APIRouter()


@router.get("/health", response_model=DetailedHealthResponse, summary="Subsystem Health Check")
async def get_subsystem_health() -> DetailedHealthResponse:
    """
    Detailed subsystem health status including PostgreSQL and Groq API readiness.
    """
    db_ok = False
    db_details = "Not tested"
    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
            db_ok = True
            db_details = "Connected"
    except Exception as e:
        db_ok = False
        db_details = "Database offline or unreachable"

    groq_ok = bool(settings.GROQ_API_KEY)

    return DetailedHealthResponse(
        status="healthy" if db_ok or settings.ENVIRONMENT == "development" else "degraded",
        environment=settings.ENVIRONMENT,
        version=settings.VERSION,
        phase=settings.PHASE,
        subsystems=SubsystemStatus(
            database=db_ok,
            groq_configured=groq_ok,
            details={
                "database_status": db_details,
                "groq_model": settings.GROQ_MODEL,
                "groq_configured": groq_ok
            }
        )
    )
