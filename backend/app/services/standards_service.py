from typing import List, Optional
from app.schemas.intelligence import (
    StandardListItem,
    StandardDetailResponse,
    StandardSectionItem
)
from app.services.data_providers import get_bis_data_provider


class StandardsService:
    """
    Standards Explorer and Standard Details service.
    Delegates querying to decoupled BaseBISDataProvider abstraction with multilingual localization.
    """

    def search_standards(
        self,
        query: Optional[str] = None,
        division: Optional[str] = None,
        qco_only: Optional[bool] = None,
        limit: int = 50,
        language: str = "en"
    ) -> List[StandardListItem]:
        provider = get_bis_data_provider()
        return provider.search_standards(query=query, division=division, qco_only=qco_only, limit=limit, language=language)

    def get_standard_details(self, standard_id_or_number: str, language: str = "en") -> Optional[StandardDetailResponse]:
        provider = get_bis_data_provider()
        return provider.get_standard_details(standard_id_or_number, language=language)


standards_service = StandardsService()
