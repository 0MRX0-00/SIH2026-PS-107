import logging
from fastapi import APIRouter, HTTPException, Depends, status
from typing import Optional
from app.schemas.chat import (
    ChatRequest,
    ChatResponse,
    ChatDebugResponse,
)
from app.services.rag_service import RAGService

logger = logging.getLogger("ebis_sahayak.chat_api")
router = APIRouter()


_rag_service: Optional[RAGService] = None


def get_rag_service() -> RAGService:
    global _rag_service
    if _rag_service is None:
        _rag_service = RAGService()
    return _rag_service


@router.post(
    "",
    response_model=ChatResponse,
    status_code=status.HTTP_200_OK,
    summary="Grounded conversational assistant query (e-BIS Sahayak RAG)",
    description=(
        "Executes the full RAG pipeline: Query -> Vector Retrieval -> Relevance Filtering -> "
        "Context Assembly -> Groq LPU Inference -> Citation Grounding & Validation."
    ),
)
async def chat_endpoint(
    request: ChatRequest,
    service: RAGService = Depends(get_rag_service),
) -> ChatResponse:
    """Handles user conversational inquiries with strict source citations and anti-hallucination guardrails."""
    if not request.message or not request.message.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Message cannot be empty."
        )

    if len(request.message) > 1000:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Message exceeds maximum allowed limit of 1000 characters."
        )

    try:
        response = await service.answer_query(request)
        return response
    except Exception as e:
        logger.exception(f"Error in chat endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while processing your request: {str(e)}"
        )


@router.post(
    "/debug",
    response_model=ChatDebugResponse,
    status_code=status.HTTP_200_OK,
    summary="RAG Pipeline Observability & Debug Endpoint",
    description="Returns detailed traces of retrieved chunks, assembled context, raw LLM outputs, and citation validations for developer inspection.",
)
async def chat_debug_endpoint(
    request: ChatRequest,
    service: RAGService = Depends(get_rag_service),
) -> ChatDebugResponse:
    """Developer endpoint to inspect intermediate stages of the RAG pipeline."""
    if not request.message or not request.message.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Message cannot be empty."
        )

    try:
        debug_response = await service.answer_query_debug(request)
        return debug_response
    except Exception as e:
        logger.exception(f"Error in chat debug endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Debug pipeline error: {str(e)}"
        )

