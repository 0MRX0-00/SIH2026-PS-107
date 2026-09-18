from fastapi import APIRouter
from app.api.v1.endpoints import (
    health,
    retrieval,
    chat,
    product_discovery,
    standards,
    certification,
    laboratories,
    language,
    feedback,
    admin,
)

api_v1_router = APIRouter()

# Register endpoint routers
api_v1_router.include_router(health.router, tags=["Health & Status"])
api_v1_router.include_router(language.router, prefix="/language", tags=["Multilingual Intelligence"])
api_v1_router.include_router(retrieval.router, prefix="/retrieval", tags=["Knowledge Retrieval"])
api_v1_router.include_router(chat.router, prefix="/chat", tags=["RAG Conversational Assistant"])
api_v1_router.include_router(product_discovery.router, prefix="/discovery", tags=["Product-to-Standard Discovery"])
api_v1_router.include_router(standards.router, prefix="/standards", tags=["Standards Explorer"])
api_v1_router.include_router(certification.router, prefix="/certification", tags=["Certification Navigator"])
api_v1_router.include_router(laboratories.router, prefix="/laboratories", tags=["Laboratory Guidance"])
api_v1_router.include_router(feedback.router, prefix="/feedback", tags=["User Feedback"])
api_v1_router.include_router(admin.router, prefix="/admin", tags=["Knowledge & Admin Management"])
