
"""
RecruitFlow AI - Document Extraction Module

Supports:
- TXT
- PDF (text-based)
- DOCX

Returns structured extraction results.
No OCR or candidate screening is performed here.
"""

from dataclasses import dataclass, field, asdict
from pathlib import Path
import io
import re
import zipfile

import pymupdf
from docx import Document


MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
MAX_EXTRACTED_CHARACTERS = 500_000
SUPPORTED_FORMATS = {".txt", ".pdf", ".docx"}


class DocumentExtractionError(Exception):
    """Raised when a document cannot be safely extracted."""


@dataclass
class ExtractionResult:
    filename: str
    file_type: str
    text: str
    character_count: int
    page_count: int | None = None
    warnings: list[str] = field(default_factory=list)

    def to_dict(self):
        return asdict(self)


def normalize_text(text: str) -> str:
    """
    Normalize whitespace without removing meaningful line breaks.
    """
    if not isinstance(text, str):
        raise DocumentExtractionError(
            "Extracted content must be text."
        )

    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = text.replace("\x00", "")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n[ \t]+", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def validate_document(filename: str, content: bytes) -> str:
    """
    Validate extension, content type, size and basic file signature.
    """
    if not isinstance(filename, str) or not filename.strip():
        raise DocumentExtractionError(
            "A valid filename is required."
        )

    extension = Path(filename).suffix.lower()

    if extension not in SUPPORTED_FORMATS:
        raise DocumentExtractionError(
            f"Unsupported format: {extension or 'none'}. "
            "Supported formats: TXT, PDF, DOCX."
        )

    if not isinstance(content, bytes):
        raise DocumentExtractionError(
            "Document content must be bytes."
        )

    if not content:
        raise DocumentExtractionError(
            "The uploaded document is empty."
        )

    if len(content) > MAX_FILE_SIZE:
        raise DocumentExtractionError(
            "Document exceeds the 10 MB size limit."
        )

    if extension == ".pdf":
        if not content.startswith(b"%PDF-"):
            raise DocumentExtractionError(
                "Invalid PDF file signature."
            )

    if extension == ".docx":
        if not zipfile.is_zipfile(io.BytesIO(content)):
            raise DocumentExtractionError(
                "Invalid DOCX file structure."
            )

        try:
            with zipfile.ZipFile(io.BytesIO(content)) as archive:
                if "word/document.xml" not in archive.namelist():
                    raise DocumentExtractionError(
                        "DOCX is missing its main document."
                    )
        except (zipfile.BadZipFile, OSError) as exc:
            raise DocumentExtractionError(
                "The DOCX file is corrupted."
            ) from exc

    return extension


def extract_txt(content: bytes) -> tuple[str, int | None, list[str]]:
    """
    Decode UTF-8 TXT, including UTF-8 BOM.
    """
    try:
        text = content.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise DocumentExtractionError(
            "TXT must use UTF-8 encoding."
        ) from exc

    return text, None, []


def extract_pdf(content: bytes) -> tuple[str, int | None, list[str]]:
    """
    Extract text from a text-based PDF.
    Scanned PDFs without embedded text require OCR.
    """
    warnings = []

    try:
        with pymupdf.open(
            stream=content, filetype="pdf"
        ) as document:
            if document.needs_pass:
                raise DocumentExtractionError(
                    "Password-protected PDFs are not supported."
                )

            page_count = len(document)

            if page_count == 0:
                raise DocumentExtractionError(
                    "PDF contains no pages."
                )

            pages = []

            for page in document:
                pages.append(page.get_text("text"))

    except DocumentExtractionError:
        raise

    except Exception as exc:
        raise DocumentExtractionError(
            "Unable to read PDF. The file may be corrupted."
        ) from exc

    text = "\n\n".join(pages)

    if not text.strip():
        raise DocumentExtractionError(
            "No extractable text found. "
            "This may be a scanned PDF requiring OCR."
        )

    if any(not page.strip() for page in pages):
        warnings.append(
            "One or more PDF pages contain no extractable text."
        )

    return text, page_count, warnings


def extract_docx(content: bytes) -> tuple[str, int | None, list[str]]:
    """
    Extract paragraphs and tables from a DOCX file.
    """
    try:
        document = Document(io.BytesIO(content))

        parts = []

        for block in document.iter_inner_content():
            if hasattr(block, "rows"):
                for row in block.rows:
                    cells = [
                        cell.text.strip()
                        for cell in row.cells
                    ]
                    parts.append(" | ".join(cells))
            else:
                parts.append(block.text)

        text = "\n".join(parts)

    except Exception as exc:
        raise DocumentExtractionError(
            "Unable to read DOCX. "
            "The file may be corrupted."
        ) from exc

    return text, None, []


def extract_document(
    filename: str,
    content: bytes
) -> ExtractionResult:
    """
    Main extraction entry point for uploaded document bytes.
    """
    extension = validate_document(filename, content)

    if extension == ".txt":
        raw_text, page_count, warnings = extract_txt(content)

    elif extension == ".pdf":
        raw_text, page_count, warnings = extract_pdf(content)

    elif extension == ".docx":
        raw_text, page_count, warnings = extract_docx(content)

    else:
        raise DocumentExtractionError(
            "Unsupported document format."
        )

    text = normalize_text(raw_text)

    if not text:
        raise DocumentExtractionError(
            "No readable text found in document."
        )

    if len(text) > MAX_EXTRACTED_CHARACTERS:
        raise DocumentExtractionError(
            "Extracted text exceeds the processing limit."
        )

    return ExtractionResult(
        filename=Path(filename).name,
        file_type=extension.lstrip(".").upper(),
        text=text,
        character_count=len(text),
        page_count=page_count,
        warnings=warnings,
    )


def extract_from_path(file_path: str | Path) -> ExtractionResult:
    """
    Convenience wrapper for local files.
    """
    path = Path(file_path)

    if not path.is_file():
        raise DocumentExtractionError(
            f"File not found: {path}"
        )

    if path.stat().st_size > MAX_FILE_SIZE:
        raise DocumentExtractionError(
            "Document exceeds the 10 MB size limit."
        )

    try:
        content = path.read_bytes()
    except OSError as exc:
        raise DocumentExtractionError(
            "Unable to read the selected file."
        ) from exc

    return extract_document(path.name, content)
