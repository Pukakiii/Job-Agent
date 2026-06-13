"""Pure, synchronous CV text extraction. CPU-bound and blocking — callers MUST run
these off the event loop via anyio.to_thread.run_sync (see CVParsingService)."""
import io

from docx import Document
from pypdf import PdfReader

PDF_MIME = "application/pdf"
DOCX_MIME = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"


def extract_pdf(data: bytes) -> str:
    reader = PdfReader(io.BytesIO(data))
    return "\n".join((page.extract_text() or "") for page in reader.pages).strip()


def extract_docx(data: bytes) -> str:
    doc = Document(io.BytesIO(data))
    return "\n".join(p.text for p in doc.paragraphs).strip()


def extract_text(content_type: str, data: bytes) -> str:
    """Dispatch on the (sniffed) content type stored on the cvs row."""
    if content_type == PDF_MIME:
        return extract_pdf(data)
    if content_type == DOCX_MIME:
        return extract_docx(data)
    raise ValueError(f"Unsupported content type for extraction: {content_type}")
