import re
import uuid
from typing import List, Dict, Any, Optional
from app.services.document_parser import ExtractedPage


class DocumentChunk:
    def __init__(
        self,
        chunk_id: str,
        document_id: str,
        text: str,
        page_start: int,
        page_end: int,
        standard_number: str,
        title: str,
        section: Optional[str] = None,
        clause: Optional[str] = None,
        source: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        self.chunk_id = chunk_id
        self.document_id = document_id
        self.text = text
        self.page_start = page_start
        self.page_end = page_end
        self.standard_number = standard_number
        self.title = title
        self.section = section
        self.clause = clause
        self.source = source or "BIS"
        self.metadata = metadata or {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "chunk_id": self.chunk_id,
            "document_id": self.document_id,
            "text": self.text,
            "page_start": self.page_start,
            "page_end": self.page_end,
            "standard_number": self.standard_number,
            "title": self.title,
            "section": self.section,
            "clause": self.clause,
            "source": self.source,
            "metadata": self.metadata,
        }


class StructureAwareChunker:
    """
    Splits document pages into hierarchical chunks respecting section, clause, and paragraph boundaries.
    Enriches each chunk with contextual headers for high RAG retrieval accuracy.
    """

    # Heading detection regexes
    SECTION_RE = re.compile(r'^(?:#+\s*)?(?:Section\s+\d+|[A-Z\s]{4,})\b', re.MULTILINE | re.IGNORECASE)
    CLAUSE_RE = re.compile(r'^(?:#+\s*)?(?:Clause\s+\d+(?:\.\d+)*|\d+\.\d+(?:\.\d+)*)\s*[:\-—]?\s*(.*)', re.MULTILINE | re.IGNORECASE)

    def __init__(
        self,
        target_chunk_size: int = 700,
        chunk_overlap: int = 100,
        min_chunk_size: int = 80
    ):
        self.target_chunk_size = target_chunk_size
        self.chunk_overlap = chunk_overlap
        self.min_chunk_size = min_chunk_size

    def chunk_pages(
        self,
        pages: List[ExtractedPage],
        doc_metadata: Dict[str, Any]
    ) -> List[DocumentChunk]:
        chunks: List[DocumentChunk] = []
        document_id = doc_metadata.get("document_id", "doc-unknown")
        standard_number = doc_metadata.get("standard_number", "IS UNKNOWN")
        doc_title = doc_metadata.get("title", "")
        source_name = doc_metadata.get("source_name", "BIS")

        current_section = "General"
        current_clause = None

        for page in pages:
            page_text = page.text
            if not page_text or page.is_scanned:
                continue

            # Split page text into structural blocks by double newlines or clause markers
            paragraphs = re.split(r'\n\s*\n', page_text)

            for para in paragraphs:
                para_clean = para.strip()
                if not para_clean:
                    continue

                # Detect Section header
                sec_match = self.SECTION_RE.search(para_clean)
                if sec_match:
                    first_line = para_clean.split('\n')[0].replace('#', '').strip()
                    current_section = first_line

                # Detect Clause header
                clause_match = self.CLAUSE_RE.search(para_clean)
                if clause_match:
                    first_line = para_clean.split('\n')[0].replace('#', '').strip()
                    current_clause = first_line

                # Build contextual header
                context_header = f"[{standard_number} | {current_section}"
                if current_clause:
                    context_header += f" | {current_clause}"
                context_header += f" | Page {page.page_number}]\n"

                # If paragraph fits comfortably in one chunk
                if len(para_clean) <= self.target_chunk_size:
                    enriched_text = context_header + para_clean
                    chunk = DocumentChunk(
                        chunk_id=f"chunk-{uuid.uuid4().hex[:12]}",
                        document_id=document_id,
                        text=enriched_text,
                        page_start=page.page_number,
                        page_end=page.page_number,
                        standard_number=standard_number,
                        title=doc_title,
                        section=current_section,
                        clause=current_clause,
                        source=source_name,
                        metadata={
                            "document_type": doc_metadata.get("document_type"),
                            "year": doc_metadata.get("year"),
                            "division": doc_metadata.get("division"),
                            "raw_text_length": len(para_clean),
                        }
                    )
                    chunks.append(chunk)
                else:
                    # Split longer paragraphs into windowed chunks
                    words = para_clean.split()
                    step = max(50, int(self.target_chunk_size / 6))
                    for i in range(0, len(words), step):
                        sub_para = " ".join(words[i:i + step + 20])
                        if len(sub_para) < self.min_chunk_size and chunks:
                            continue
                        enriched_text = context_header + sub_para
                        chunk = DocumentChunk(
                            chunk_id=f"chunk-{uuid.uuid4().hex[:12]}",
                            document_id=document_id,
                            text=enriched_text,
                            page_start=page.page_number,
                            page_end=page.page_number,
                            standard_number=standard_number,
                            title=doc_title,
                            section=current_section,
                            clause=current_clause,
                            source=source_name,
                            metadata={
                                "document_type": doc_metadata.get("document_type"),
                                "year": doc_metadata.get("year"),
                                "division": doc_metadata.get("division"),
                                "is_subchunk": True,
                            }
                        )
                        chunks.append(chunk)

        return chunks
