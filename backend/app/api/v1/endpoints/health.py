from fastapi import APIRouter
from sqlalchemy import text
from app.core.config import settings
from app.db.session import AsyncSessionLocal
from app.schemas.health import DetailedHealthResponse, SubsystemStatus

router = APIRouter()


@router.get("/health", response_model=DetailedHealthResponse, summary="Subsystem Health Check")
async def get_subsystem_health() -> DetailedHealthResponse:
    """
    Detailed subsystem health status including PostgreSQL and Qdrant readiness.
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

    # Vector store configuration check
    vector_configured = bool(settings.QDRANT_HOST and settings.QDRANT_PORT)

    return DetailedHealthResponse(
        status="healthy" if db_ok or settings.ENVIRONMENT == "development" else "degraded",
        environment=settings.ENVIRONMENT,
        version=settings.VERSION,
        phase=settings.PHASE,
        subsystems=SubsystemStatus(
            database=db_ok,
            vector_store_configured=vector_configured,
            embedding_provider=settings.EMBEDDING_PROVIDER,
            details={
                "database_status": db_details,
                "qdrant_host": f"{settings.QDRANT_HOST}:{settings.QDRANT_PORT}",
                "groq_configured": bool(settings.GROQ_API_KEY)
            }
        )
    )
