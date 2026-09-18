import hashlib
import os
from pathlib import Path
from typing import Dict, Any, Optional, Tuple

SUPPORTED_EXTENSIONS = {".pdf", ".md", ".txt"}
MAX_FILE_SIZE_BYTES = 50 * 1024 * 1024  # 50 MB limit


class DocumentLoaderError(Exception):
    """Exception raised for errors during document loading and validation."""
    pass


class DocumentLoader:
    """
    Validates, reads, and generates cryptographically secure hashes for files.
    Ensures safe filesystem access and idempotency checks.
    """

    @staticmethod
    def compute_sha256(filepath: Path) -> str:
        """Computes SHA-256 hash of a file for idempotency tracking."""
        sha256_hash = hashlib.sha256()
        with open(filepath, "rb") as f:
            for byte_block in iter(lambda: f.read(65536), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    @staticmethod
    def validate_and_inspect(filepath: Path) -> Dict[str, Any]:
        """
        Validates the file existence, type, and size constraints.
        Returns file inspection metadata.
        """
        if not filepath.exists():
            raise DocumentLoaderError(f"File not found: {filepath}")

        if not filepath.is_file():
            raise DocumentLoaderError(f"Path is not a regular file: {filepath}")

        ext = filepath.suffix.lower()
        if ext not in SUPPORTED_EXTENSIONS:
            raise DocumentLoaderError(
                f"Unsupported file format '{ext}'. Supported formats: {', '.join(SUPPORTED_EXTENSIONS)}"
            )

        file_size = filepath.stat().st_size
        if file_size == 0:
            raise DocumentLoaderError(f"File is empty: {filepath}")

        if file_size > MAX_FILE_SIZE_BYTES:
            raise DocumentLoaderError(
                f"File size ({file_size / (1024*1024):.2f} MB) exceeds maximum allowed size ({MAX_FILE_SIZE_BYTES / (1024*1024)} MB)"
            )

        file_hash = DocumentLoader.compute_sha256(filepath)

        return {
            "filename": filepath.name,
            "filepath": str(filepath.resolve()),
            "extension": ext,
            "file_size_bytes": file_size,
            "file_hash_sha256": file_hash,
        }
