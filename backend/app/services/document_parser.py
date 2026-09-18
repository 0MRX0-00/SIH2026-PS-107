import re
from pathlib import Path
from typing import List, Dict, Any, Optional
from pypdf import PdfReader


class DocumentParserError(Exception):
    """Exception raised when document parsing fails."""
    pass


class ExtractedPage:
    def __init__(self, page_number: int, text: str, is_scanned: bool = False):
        self.page_number = page_number
        self.text = text
        self.is_scanned = is_scanned

    def to_dict(self) -> Dict[str, Any]:
        return {
            "page_number": self.page_number,
            "text": self.text,
            "is_scanned": self.is_scanned,
        }


class DocumentParser:
    """
    Parses PDF, Markdown, and TXT documents into page-aware structural text representations.
    """

    @classmethod
    def parse(cls, filepath: Path) -> List[ExtractedPage]:
        ext = filepath.suffix.lower()
        if ext == ".pdf":
            return cls.parse_pdf(filepath)
        elif ext in {".md", ".txt"}:
            return cls.parse_text_or_markdown(filepath)
        else:
            raise DocumentParserError(f"Unsupported file format: {ext}")

    @classmethod
    def parse_pdf(cls, filepath: Path) -> List[ExtractedPage]:
        """Extracts text per page from PDF using pypdf, detecting scanned pages."""
        try:
            reader = PdfReader(str(filepath))
            pages: List[ExtractedPage] = []

            for idx, page in enumerate(reader.pages):
                page_num = idx + 1
                try:
                    text = page.extract_text() or ""
                except Exception:
                    text = ""

                clean_text = text.strip()
                is_scanned = len(clean_text) < 20  # Flag likely image/scanned page requiring OCR
                pages.append(ExtractedPage(page_number=page_num, text=clean_text, is_scanned=is_scanned))

            if not pages:
                raise DocumentParserError(f"PDF contains no readable pages: {filepath}")

            return pages
        except Exception as e:
            if isinstance(e, DocumentParserError):
                raise
            raise DocumentParserError(f"Failed to parse PDF {filepath}: {str(e)}")

    @classmethod
    def parse_text_or_markdown(cls, filepath: Path) -> List[ExtractedPage]:
        """Parses Markdown or plain text, respecting explicit [PAGE X] markers if present."""
        try:
            with open(filepath, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()

            # Check if explicit page markers exist (e.g., [PAGE 1], [PAGE 2])
            page_pattern = re.compile(r'\[PAGE\s+(\d+)\]', re.IGNORECASE)
            matches = list(page_pattern.finditer(content))

            if matches:
                pages: List[ExtractedPage] = []
                for i, match in enumerate(matches):
                    page_num = int(match.group(1))
                    start_idx = match.end()
                    end_idx = matches[i + 1].start() if i + 1 < len(matches) else len(content)
                    page_text = content[start_idx:end_idx].strip()
                    pages.append(ExtractedPage(page_number=page_num, text=page_text, is_scanned=False))
                return pages
            else:
                # Default: treat whole document as page 1
                return [ExtractedPage(page_number=1, text=content.strip(), is_scanned=False)]
        except Exception as e:
            raise DocumentParserError(f"Failed to parse text document {filepath}: {str(e)}")
