from fastapi import APIRouter, HTTPException, Depends
from typing import Optional

from app.schemas.retrieval import SearchRequest, SearchResponse, SearchResultItem
from app.services.retrieval_service import RetrievalService

router = APIRouter()

_retrieval_service: Optional[RetrievalService] = None


def get_retrieval_service() -> RetrievalService:
    global _retrieval_service
    if _retrieval_service is None:
        _retrieval_service = RetrievalService()
    return _retrieval_service


@router.post(
    "/search",
    response_model=SearchResponse,
    summary="Semantic Vector Retrieval against BIS Knowledge Base",
    description="Performs semantic vector search against indexed Indian Standards, QCOs, and certification guidelines. Returns ranked chunks with exact clause and page metadata. (No LLM generation in Phase 2)."
)
async def search_knowledge_base(
    request: SearchRequest,
    service: RetrievalService = Depends(get_retrieval_service)
) -> SearchResponse:
    try:
        results = service.search(
            query=request.query,
            top_k=request.top_k,
            standard_number=request.standard_number,
            document_type=request.document_type,
            language=request.language
        )

        items = [
            SearchResultItem(
                chunk_id=r.get("chunk_id", ""),
                document_id=r.get("document_id"),
                score=r.get("score", 0.0),
                text=r.get("text", ""),
                standard_number=r.get("standard_number"),
                title=r.get("title"),
                section=r.get("section"),
                clause=r.get("clause"),
                page_start=r.get("page_start"),
                page_end=r.get("page_end"),
                source=r.get("source", "BIS"),
                metadata=r.get("metadata", {})
            )
            for r in results
        ]

        return SearchResponse(
            query=request.query,
            total_results=len(items),
            results=items,
            retrieval_mode="Semantic Vector Search (Qdrant)"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error performing vector retrieval: {str(e)}"
        )
