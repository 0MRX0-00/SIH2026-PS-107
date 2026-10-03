"""
Seed BIS Data Provider with Provenance Tagging.
Extends SeedBISDataProvider to attach explicit provenance metadata tags indicating
curated BIS gazette registry origin, preserving fast deterministic response times.
(Note: True live HTTP web scraping of bis.gov.in / manakonline.in is not implemented;
this provider uses the local verified seed registry with provenance metadata).
"""
import logging
from typing import List, Dict, Any, Optional
from app.services.data_providers.seed_provider import SeedBISDataProvider
from app.schemas.intelligence import StandardListItem

logger = logging.getLogger(__name__)


class SeedProviderWithProvenanceTag(SeedBISDataProvider):
    """
    Seed BIS Data Provider with Provenance Tagging.
    Decorates seed records with explicit verification metadata and provenance tags.
    """

    def get_evidence_provenance(self, record: Dict[str, Any]) -> Dict[str, Any]:
        prov = super().get_evidence_provenance(record)
        prov["provenance"] = prov["provenance"] + " [Curated BIS Registry via Provider Adapter]"
        return prov

    def search_standards(
        self,
        query: Optional[str] = None,
        division: Optional[str] = None,
        qco_only: Optional[bool] = None,
        limit: int = 50,
        language: str = "en"
    ) -> List[StandardListItem]:
        return super().search_standards(query=query, division=division, qco_only=qco_only, limit=limit, language=language)


# Alias for backward compatibility with existing tests
LiveBISDataProvider = SeedProviderWithProvenanceTag
