from typing import List, Optional
from app.schemas.intelligence import (
    LaboratorySearchRequest,
    LaboratorySearchResponse,
    LaboratoryItem
)
from app.services.data_providers import get_bis_data_provider


class LaboratoryService:
    """
    Structured laboratory guidance and search service.
    Delegates querying to BaseBISDataProvider abstraction with multilingual localization.
    """

    def search_laboratories(self, request: LaboratorySearchRequest) -> LaboratorySearchResponse:
        provider = get_bis_data_provider()
        return provider.search_laboratories(request)

    def list_all(self, language: str = "en") -> List[LaboratoryItem]:
        provider = get_bis_data_provider()
        return provider.list_all_laboratories(language=language)


laboratory_service = LaboratoryService()
