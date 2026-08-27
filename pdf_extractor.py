from pathlib import Path
from typing import NamedTuple
from pypdf import PdfReader


class PDFDocument(NamedTuple):
    """Holds metadata and extracted text from a PDF file."""
    file_path: str
    page_count: int
    char_count: int
    content: str


class PDFExtractor:
    """Handles loading and extracting text from PDF documents."""

    @staticmethod
    def extract(file_path: str | Path) -> PDFDocument:
        """Extract text and metadata from a PDF file.

        Args:
            file_path: Path to the PDF file.

        Returns:
            PDFDocument with metadata and extracted text.

        Raises:
            FileNotFoundError: If the PDF file does not exist.
            ValueError: If the PDF contains no extractable text.
        """
        path = Path(file_path)
        if not path.is_file():
            raise FileNotFoundError(f"PDF file not found at: {file_path}")

        reader = PdfReader(str(path))
        page_count = len(reader.pages)

        extracted_pages = []
        for i, page in enumerate(reader.pages, start=1):
            text = page.extract_text() or ""
            extracted_pages.append(text)

        content = "\n".join(extracted_pages).strip()

        if not content:
            raise ValueError(
                "The PDF was loaded successfully, but no text could be extracted. "
                "It may contain scanned images or be password-protected."
            )

        return PDFDocument(
            file_path=str(path),
            page_count=page_count,
            char_count=len(content),
            content=content
        )
