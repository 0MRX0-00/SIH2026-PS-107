#!/usr/bin/env python3
"""
e-BIS Sahayak: Document Ingestion CLI Tool
Usage:
    python -m app.cli.ingest --path data/sample/
    python -m app.cli.ingest --path data/raw/is_1293.pdf --force
"""

import argparse
import sys
import os
from pathlib import Path
import json

import logging

from app.services.ingestion_pipeline import get_ingestion_pipeline


def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
    parser = argparse.ArgumentParser(
        description="e-BIS Sahayak Knowledge Ingestion CLI (SIH 2026)"
    )
    parser.add_argument(
        "--path",
        "-p",
        type=str,
        required=True,
        help="Path to a document file (.pdf, .md, .txt) or directory containing documents to ingest."
    )
    parser.add_argument(
        "--force",
        "-f",
        action="store_true",
        help="Force re-indexing even if file hash is unchanged."
    )

    args = parser.parse_args()
    target_path = Path(args.path)

    if not target_path.exists():
        print(f"Error: Path does not exist: {target_path}", file=sys.stderr)
        sys.exit(1)

    pipeline = get_ingestion_pipeline()

    print("=" * 70)
    print("e-BIS Sahayak: Knowledge Ingestion Pipeline")
    print(f"Target: {target_path} | Force Reindex: {args.force}")
    print("=" * 70)

    if target_path.is_file():
        res = pipeline.ingest_file(target_path, force_reindex=args.force)
        results = [res]
    else:
        results = pipeline.ingest_directory(target_path, force_reindex=args.force)

    print("\n" + "=" * 70)
    print("INGESTION SUMMARY:")
    print("=" * 70)
    for r in results:
        status = r.get("status", "UNKNOWN")
        filename = r.get("filename", "Unknown")
        chunks = r.get("chunks_created", 0)
        std = r.get("standard_number", "N/A")
        print(f"  [{status}] {filename} -> Standard: {std} | Chunks: {chunks}")

    print("=" * 70)
    success_count = sum(1 for r in results if r.get("status") in {"SUCCESS", "UNCHANGED"})
    print(f"Total Processed: {len(results)} | Successful: {success_count}")
    print("=" * 70)


if __name__ == "__main__":
    main()
