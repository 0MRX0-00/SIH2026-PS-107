import logging
from fastapi import APIRouter, HTTPException, Depends, status
from typing import Optional
from app.schemas.chat import (
    ChatRequest,
    ChatResponse,
    ChatDebugResponse,
)
from app.services.query_service import QueryService, query_service

logger = logging.getLogger("ebis_sahayak.chat_api")
router = APIRouter()


def get_query_service() -> QueryService:
    return query_service


@router.post(
    "",
    response_model=ChatResponse,
    status_code=status.HTTP_200_OK,
    summary="Groq AI Assistant query (e-BIS Sahayak)",
    description="Executes Groq AI Assistant pipeline: Input Validation -> Intent Routing -> Context Assembly -> Groq Inference -> Response Normalization.",
)
async def chat_endpoint(
    request: ChatRequest,
    service: QueryService = Depends(get_query_service),
) -> ChatResponse:
    """Handles user conversational inquiries with Groq AI Assistant architecture."""
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
        response = await service.process_query(request)
        return response
    except Exception as e:
        logger.exception(f"Error in chat endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while processing your request. Please try again or contact system support."
        )


@router.post(
    "/debug",
    response_model=ChatDebugResponse,
    status_code=status.HTTP_200_OK,
    summary="Groq Pipeline Observability & Debug Endpoint",
    description="Returns detailed traces of intent classification, system prompt, assembled messages, and raw LLM output.",
)
async def chat_debug_endpoint(
    request: ChatRequest,
    service: QueryService = Depends(get_query_service),
) -> ChatDebugResponse:
    """Developer endpoint to inspect intermediate stages of the Groq pipeline."""
    if not request.message or not request.message.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Message cannot be empty."
        )

    try:
        debug_response = await service.get_debug_info(request)
        return debug_response
    except Exception as e:
        logger.exception(f"Error in chat debug endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred in debug pipeline processing."
        )
