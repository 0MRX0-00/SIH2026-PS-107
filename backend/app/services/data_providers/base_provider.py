"""
Abstract Base BIS Data Provider Interface.
Establishes a decoupled, future-proof data abstraction layer for BIS standard lookup,
certification schemes, laboratory discovery, and claim verification.
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from app.schemas.chat import SourceItem
from app.schemas.intelligence import (
    StandardListItem,
    StandardDetailResponse,
    LaboratoryItem,
    LaboratorySearchResponse,
    LaboratorySearchRequest,
    CandidateStandardItem
)


class BaseBISDataProvider(ABC):
    """Abstract Base Class for BIS Data Providers."""

    @abstractmethod
    def search_standards(
        self,
        query: Optional[str] = None,
        division: Optional[str] = None,
        qco_only: Optional[bool] = None,
        limit: int = 50,
        language: str = "en"
    ) -> List[StandardListItem]:
        """Search Indian Standards catalog."""
        pass

    @abstractmethod
    def get_standard_details(
        self,
        standard_id_or_number: str,
        language: str = "en"
    ) -> Optional[StandardDetailResponse]:
        """Retrieve detailed Indian Standard record by ID or number."""
        pass

    @abstractmethod
    def discover_product_standards(
        self,
        product_description: str,
        material: Optional[str] = None,
        intended_use: Optional[str] = None,
        max_candidates: int = 5,
        language: str = "en"
    ) -> List[CandidateStandardItem]:
        """Discover candidate standards for a given product description."""
        pass

    @abstractmethod
    def search_laboratories(
        self,
        request: LaboratorySearchRequest
    ) -> LaboratorySearchResponse:
        """Search recognized/accredited testing laboratories."""
        pass

    @abstractmethod
    def list_all_laboratories(
        self,
        language: str = "en"
    ) -> List[LaboratoryItem]:
        """List all accredited laboratories in catalog."""
        pass

    @abstractmethod
    def list_all_schemes(
        self,
        language: str = "en"
    ) -> List[Dict[str, Any]]:
        """List certification schemes (Scheme-I, Scheme-II, Scheme-IV)."""
        pass

    @abstractmethod
    def get_evidence_provenance(
        self,
        record: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Extract explicit data provenance metadata for a record."""
        pass
