from fastapi import APIRouter, HTTPException, Depends
from app.schemas.intelligence import ProductDiscoveryRequest, ProductDiscoveryResponse
from app.services.product_discovery_service import ProductDiscoveryService
from app.services.retrieval_service import RetrievalService
from app.services.groq_service import GroqService
from app.services.citation_engine import CitationEngine
from app.services.embedding_service import FastEmbedService, FallbackDeterministicEmbeddingService
from app.services.vector_store import VectorStoreService

router = APIRouter()

def get_product_discovery_service() -> ProductDiscoveryService:
    try:
        embedder = FastEmbedService()
    except Exception:
        embedder = FallbackDeterministicEmbeddingService()
    
    vector_store = VectorStoreService()
    retrieval_service = RetrievalService(embedder, vector_store)
    groq_service = GroqService()
    citation_engine = CitationEngine()
    
    return ProductDiscoveryService(
        retrieval_service=retrieval_service,
        groq_service=groq_service,
        citation_engine=citation_engine
    )

@router.post("/product-to-standard", response_model=ProductDiscoveryResponse)
def discover_product_standards(
    request: ProductDiscoveryRequest,
    service: ProductDiscoveryService = Depends(get_product_discovery_service)
):
    """
    Intelligently discover applicable Indian Standards based on natural language product specifications.
    Triggers clarification prompts if product description is ambiguous.
    """
    try:
        return service.discover(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Discovery failed: {str(e)}")
