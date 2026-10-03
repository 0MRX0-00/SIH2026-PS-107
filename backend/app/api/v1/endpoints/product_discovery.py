import logging
from fastapi import APIRouter, HTTPException, Depends, status
from app.schemas.intelligence import ProductDiscoveryRequest, ProductDiscoveryResponse
from app.services.product_discovery_service import ProductDiscoveryService, product_discovery_service

logger = logging.getLogger("ebis_sahayak.discovery_api")
router = APIRouter()


def get_product_discovery_service() -> ProductDiscoveryService:
    return product_discovery_service


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
        return service.discover_standards(request)
    except Exception as e:
        logger.exception(f"Product discovery error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to execute product-to-standard discovery. Please verify your product input."
        )
