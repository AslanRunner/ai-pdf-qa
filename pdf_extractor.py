"""PDF text extraction module supporting single and multi-PDF directory extraction."""

from pathlib import Path
from typing import NamedTuple
from pypdf import PdfReader


class PDFDocument(NamedTuple):
    """Holds metadata and extracted text from a PDF file."""
    file_name: str
    file_path: str
    page_count: int
    char_count: int
    content: str


class PDFExtractor:
    """Handles loading and extracting text from single or multiple PDF documents."""

    @staticmethod
    def extract_file(file_path: str | Path) -> PDFDocument:
        """Extract text and metadata from a single PDF file.

        Args:
            file_path: Path to the PDF file.

        Returns:
            PDFDocument with metadata and extracted text.

        Raises:
            FileNotFoundError: If the PDF file does not exist.
            ValueError: If no text could be extracted.
        """
        path = Path(file_path)
        if not path.is_file():
            raise FileNotFoundError(f"PDF file not found at: {file_path}")

        reader = PdfReader(str(path))
        page_count = len(reader.pages)

        extracted_pages = []
        for page in reader.pages:
            text = page.extract_text() or ""
            extracted_pages.append(text)

        content = "\n".join(extracted_pages).strip()

        if not content:
            raise ValueError(
                f"No extractable text found in '{path.name}'. "
                "It may contain scanned images or be password-protected."
            )

        return PDFDocument(
            file_name=path.name,
            file_path=str(path),
            page_count=page_count,
            char_count=len(content),
            content=content,
        )

    @staticmethod
    def extract_stream(stream, file_name: str = "document.pdf") -> PDFDocument:
        """Extract text and metadata from a file-like stream (e.g. Streamlit UploadedFile).

        Args:
            stream: A file-like object or bytes stream.
            file_name: Name of the uploaded file.

        Returns:
            PDFDocument with metadata and extracted text.
        """
        reader = PdfReader(stream)
        page_count = len(reader.pages)

        extracted_pages = []
        for page in reader.pages:
            text = page.extract_text() or ""
            extracted_pages.append(text)

        content = "\n".join(extracted_pages).strip()

        if not content:
            raise ValueError(
                f"No extractable text found in '{file_name}'. "
                "It may contain scanned images or be password-protected."
            )

        return PDFDocument(
            file_name=file_name,
            file_path=file_name,
            page_count=page_count,
            char_count=len(content),
            content=content,
        )

    @classmethod
    def extract_directory(cls, dir_path: str | Path) -> list[PDFDocument]:
        """Extract text and metadata from all PDF files in a given directory.

        Args:
            dir_path: Path to the directory containing PDFs.

        Returns:
            List of PDFDocument objects.

        Raises:
            FileNotFoundError: If the directory does not exist.
            ValueError: If no PDF files are found in the directory.
        """
        directory = Path(dir_path)
        if not directory.is_dir():
            raise FileNotFoundError(f"Directory not found: {dir_path}")

        pdf_files = sorted(directory.glob("*.pdf"))
        if not pdf_files:
            raise ValueError(f"No PDF files found in directory: {dir_path}")

        documents: list[PDFDocument] = []
        for pdf_file in pdf_files:
            try:
                doc = cls.extract_file(pdf_file)
                documents.append(doc)
            except Exception as e:
                print(f"[!] Warning: Could not extract '{pdf_file.name}': {e}")

        if not documents:
            raise ValueError(f"Failed to extract text from any PDF in directory: {dir_path}")

        return documents

    @classmethod
    def extract_path(cls, path_str: str | Path) -> list[PDFDocument]:
        """Convenience method that handles either a single PDF file or a directory of PDFs."""
        target = Path(path_str)
        if target.is_dir():
            return cls.extract_directory(target)
        elif target.is_file():
            return [cls.extract_file(target)]
        else:
            raise FileNotFoundError(f"Path not found: {path_str}")
