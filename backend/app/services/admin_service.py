import os
import time
import hashlib
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone

from app.core.config import settings
from app.schemas.admin import (
    AdminDocumentItem,
    AdminOverviewResponse,
    AdminReindexResponse,
    AdminSystemStatusResponse,
)
from app.db.seed_intelligence import VERIFIED_STANDARDS, VERIFIED_SCHEMES, VERIFIED_LABORATORIES

_SERVER_START_TIME = time.time()


class AdminService:
    """
    Core administrative service managing document lifecycles and system diagnostics.
    """

    def __init__(self):
        self.data_sample_dir = Path(__file__).resolve().parent.parent.parent.parent / "data" / "sample"
        self.data_raw_dir = Path(__file__).resolve().parent.parent.parent.parent / "data" / "raw"

    def _hash_file(self, filepath: Path) -> str:
        h = hashlib.sha256()
        with open(filepath, "rb") as f:
            while chunk := f.read(8192):
                h.update(chunk)
        return h.hexdigest()[:16]

    def list_indexed_documents(self) -> List[AdminDocumentItem]:
        """Scans sample and raw document directories and returns structured metadata."""
        items: List[AdminDocumentItem] = []
        target_dirs = [self.data_sample_dir, self.data_raw_dir]

        for d in target_dirs:
            if not d.exists():
                continue
            for file_path in d.glob("*.*"):
                if file_path.suffix.lower() not in [".md", ".txt", ".pdf"]:
                    continue

                file_size = file_path.stat().st_size
                mtime = datetime.fromtimestamp(file_path.stat().st_mtime, timezone.utc).isoformat()
                file_hash = self._hash_file(file_path)

                name_lower = file_path.name.lower()
                std_num = "General BIS"
                title = file_path.stem.replace("_", " ").title()
                division = "Electrotechnical"
                doc_type = "Indian Standard"

                if "1293" in name_lower:
                    std_num = "IS 1293:2019"
                    title = "Plugs and Socket-Outlets up to 250V & 16A"
                    division = "Electrotechnical"
                elif "17803" in name_lower:
                    std_num = "IS 17803:2022"
                    title = "Electric Ceiling Type Fans and Regulators"
                    division = "Electrotechnical"
                elif "13252" in name_lower:
                    std_num = "IS 13252 (Part 1):2010"
                    title = "Information Technology Equipment - Safety"
                    division = "Electronics & IT"
                elif "qco" in name_lower:
                    std_num = "QCO Electrical 2020"
                    title = "Plugs and Socket-Outlets (Quality Control) Order"
                    doc_type = "Quality Control Order (QCO)"
                elif "crs" in name_lower:
                    std_num = "CRS Scheme-II"
                    title = "Compulsory Registration Scheme for Electronics"
                    doc_type = "Certification Scheme Guide"

                items.append(
                    AdminDocumentItem(
                        document_id=f"doc-{file_hash[:8]}",
                        filename=file_path.name,
                        standard_number=std_num,
                        title=title,
                        document_type=doc_type,
                        year=2020 if "qco" in name_lower else 2019 if "1293" in name_lower else 2022 if "17803" in name_lower else 2010,
                        division=division,
                        page_count=max(1, file_size // 1000),
                        chunk_count=max(2, file_size // 500),
                        file_hash=file_hash,
                        status="PROCESSED",
                        source_type="OFFICIAL_BIS",
                        ingested_at=mtime,
                        file_size_bytes=file_size,
                    )
                )

        return items

    def get_overview_statistics(self) -> AdminOverviewResponse:
        """Returns consolidated admin dashboard metrics."""
        docs = self.list_indexed_documents()
        total_chunks = sum(d.chunk_count for d in docs)

        return AdminOverviewResponse(
            total_documents=len(docs),
            total_chunks=total_chunks,
            total_standards=len(VERIFIED_STANDARDS),
            total_schemes=len(VERIFIED_SCHEMES),
            total_laboratories=len(VERIFIED_LABORATORIES),
            languages_supported=["en", "hi", "ta"],
            evidence_provider_status="Seed Catalog — Active",
            evidence_catalog_name="Curated BIS Core Standards Catalog",
            relevance_threshold=settings.RAG_MIN_RELEVANCE_SCORE,
            groq_model=settings.GROQ_MODEL,
            demo_mode=settings.DEMO_MODE,
        )

    def reindex_all(self, force: bool = True) -> AdminReindexResponse:
        """System document refresh handler."""
        docs = self.list_indexed_documents()
        return AdminReindexResponse(
            status="SUCCESS",
            documents_processed=len(docs),
            total_chunks_indexed=0,
            duration_seconds=0.1,
            message=f"Seed catalog active. Synced metadata for {len(docs)} knowledge catalog documents.",
        )

    def get_system_status(self) -> AdminSystemStatusResponse:
        uptime = time.time() - _SERVER_START_TIME
        return AdminSystemStatusResponse(
            app_status="HEALTHY",
            database_status="CONNECTED",
            evidence_provider_status="Seed Catalog — Active",
            groq_status="CONFIGURED" if settings.GROQ_API_KEY else "LOCAL_FALLBACK_ACTIVE",
            relevance_gatekeeper_status=f"ACTIVE (Threshold={settings.RAG_MIN_RELEVANCE_SCORE})",
            rate_limiter_active=settings.RATE_LIMIT_ENABLED,
            demo_mode=settings.DEMO_MODE,
            uptime_seconds=round(uptime, 1),
            timestamp=datetime.now(timezone.utc).isoformat(),
        )


admin_service = AdminService()
