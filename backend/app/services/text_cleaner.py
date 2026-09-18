import re
import unicodedata


class TextCleaner:
    """
    Cleans, normalizes, and removes noise from extracted technical texts.
    """

    @staticmethod
    def clean(text: str) -> str:
        if not text:
            return ""

        # Normalize unicode characters (e.g. smart quotes, non-breaking spaces)
        text = unicodedata.normalize("NFKC", text)

        # Fix hyphenated line breaks (e.g. "require-\nments" -> "requirements")
        text = re.sub(r'(\w+)-\s*\n\s*(\w+)', r'\1\2', text)

        # Normalize multiple newlines and carriage returns
        text = re.sub(r'\r\n', '\n', text)
        text = re.sub(r'\n{3,}', '\n\n', text)

        # Normalize multiple spaces and tabs within lines
        text = re.sub(r'[ \t]+', ' ', text)

        # Remove repetitive header/footer artifacts common in standard scans
        lines = [line.strip() for line in text.split('\n')]
        cleaned_lines = []
        for line in lines:
            # Skip standalone page numbers or pure punctuation noise
            if re.match(r'^\s*[-—–\d\.\s]+\s*$', line) and len(line) < 6:
                continue
            cleaned_lines.append(line)

        return '\n'.join(cleaned_lines).strip()
