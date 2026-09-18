import re
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime, timezone
import uuid


class MetadataExtractor:
    """
    Extracts structured BIS standard metadata, QCO identifiers, and publication details.
    """

    # Regex patterns for Indian Standards & QCO Gazettes
    IS_PATTERN = re.compile(r'\b(IS(?:\s*[\/A-Z]+)*\s*\d+(?:\s*[\:\/]\s*\d{4})?)\b', re.IGNORECASE)
    QCO_PATTERN = re.compile(r'\b(S\.O\.\s*\d+\s*\([A-Z]\))\b', re.IGNORECASE)
    YEAR_PATTERN = re.compile(r'\b(19\d{2}|20\d{2})\b')

    @classmethod
    def extract_from_content(cls, filepath: Path, raw_text: str, page_count: int, file_hash: str) -> Dict[str, Any]:
        """Extracts metadata from explicit markers or regex inference."""
        metadata: Dict[str, Any] = {
            "document_id": f"doc-{uuid.uuid4().hex[:12]}",
            "title": filepath.stem.replace("_", " ").replace("-", " ").title(),
            "standard_number": None,
            "document_type": "Indian Standard",
            "year": None,
            "division": "General",
            "source_name": "Bureau of Indian Standards (BIS)",
            "source_url": None,
            "page_count": page_count,
            "language": "en",
            "file_hash_sha256": file_hash,
            "ingestion_timestamp": datetime.now(timezone.utc).isoformat(),
            "status": "PROCESSED",
        }

        # 1. Parse structured metadata header block if present (e.g. in test fixtures or markdown)
        header_match = re.search(r'(?:<!--\s*METADATA|\[DOCUMENT_METADATA\])([\s\S]*?)(?:-->|\[PAGE|\n\n)', raw_text)
        if header_match:
            block = header_match.group(1)
            for line in block.split('\n'):
                if ':' in line:
                    key, val = line.split(':', 1)
                    k = key.strip().lower()
                    v = val.strip()
                    if k in metadata and v:
                        if k == "year":
                            try:
                                metadata[k] = int(v)
                            except ValueError:
                                pass
                        else:
                            metadata[k] = v

        # 2. Infer Standard Number if not explicitly provided
        if not metadata["standard_number"]:
            is_match = cls.IS_PATTERN.search(raw_text[:2000])
            if is_match:
                metadata["standard_number"] = is_match.group(1).upper()
            else:
                qco_match = cls.QCO_PATTERN.search(raw_text[:2000])
                if qco_match:
                    metadata["standard_number"] = qco_match.group(1)
                    metadata["document_type"] = "Quality Control Order"
                else:
                    metadata["standard_number"] = filepath.stem.upper()

        # 3. Infer Year if not set
        if not metadata["year"] and metadata["standard_number"]:
            year_match = cls.YEAR_PATTERN.search(metadata["standard_number"])
            if year_match:
                metadata["year"] = int(year_match.group(1))

        return metadata
