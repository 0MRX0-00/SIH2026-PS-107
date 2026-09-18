import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.middleware import (
    RequestIDMiddleware,
    SecurityHeadersMiddleware,
    RequestBodySizeLimitMiddleware,
    RateLimitMiddleware,
)
from app.api.v1.router import api_v1_router
from app.schemas.health import RootHealthResponse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("ebis_sahayak")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup lifecycle
    logger.info(f"Starting {settings.PROJECT_NAME} v{settings.VERSION} [{settings.PHASE}]")
    logger.info(f"Environment: {settings.ENVIRONMENT} | Demo Mode: {settings.DEMO_MODE}")
    yield
    # Shutdown lifecycle
    logger.info(f"Shutting down {settings.PROJECT_NAME}")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Intelligent AI Assistant for Indian Standards and BIS Services (SIH 2026 SIH26107)",
    openapi_url="/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# 1. Request ID Tracking Middleware (Outermost)
app.add_middleware(RequestIDMiddleware)

# 2. Security Headers
app.add_middleware(SecurityHeadersMiddleware)

# 3. Request Body Size Limiter
app.add_middleware(RequestBodySizeLimitMiddleware)

# 4. API Rate Limiter
app.add_middleware(RateLimitMiddleware)

# 5. CORS Configuration
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["X-Request-ID"],
    )


# Global Exception Handler with Request ID tracking
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    req_id = getattr(request.state, "request_id", "unknown-request-id")
    logger.error(f"[{req_id}] Unhandled exception at {request.url.path}: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        headers={"X-Request-ID": req_id},
        content={
            "error": "Internal Server Error",
            "detail": "An unexpected error occurred. Please contact system support.",
            "path": request.url.path,
            "request_id": req_id
        }
    )


# Root Health Endpoint
@app.get("/health", response_model=RootHealthResponse, tags=["Health & Status"])
async def root_health() -> RootHealthResponse:
    return RootHealthResponse(
        status="healthy",
        service=settings.PROJECT_NAME,
        version=settings.VERSION,
        phase=settings.PHASE
    )


# API v1 Router inclusion
app.include_router(api_v1_router, prefix=settings.API_V1_STR)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
