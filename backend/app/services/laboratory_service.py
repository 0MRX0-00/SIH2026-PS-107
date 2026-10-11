from typing import List, Optional, Dict, Any
from app.schemas.intelligence import (
    LaboratorySearchRequest,
    LaboratorySearchResponse,
    LaboratoryItem,
    LaboratoryStatsResponse
)
from app.services.data_providers import get_bis_data_provider
from app.db.seed_intelligence import reload_verified_laboratories


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

    def get_by_id_or_code(self, id_or_code: str, language: str = "en") -> Optional[LaboratoryItem]:
        provider = get_bis_data_provider()
        return provider.get_laboratory_by_id_or_code(id_or_code, language=language)

    def get_stats(self) -> LaboratoryStatsResponse:
        provider = get_bis_data_provider()
        stats = provider.get_laboratory_stats()
        return LaboratoryStatsResponse(**stats)

    def refresh_from_source(self) -> Dict[str, Any]:
        """Trigger importer refresh and reload in-memory dataset."""
        from app.scripts.import_laboratories import BISLaboratoryImporter
        importer = BISLaboratoryImporter()
        stats = importer.import_all()
        reload_verified_laboratories()
        return stats


laboratory_service = LaboratoryService()
