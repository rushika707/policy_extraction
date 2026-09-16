import json
from pathlib import Path

from docling.document_converter import DocumentConverter


def extract_pdf_text(pdf_path: str) -> str:
    """
    Convert an arbitrary PDF using Docling and return
    structured Markdown suitable for LLM policy extraction.

    Docling preserves document hierarchy and represents
    tables in a much more useful form than raw PDF text.
    """

    pdf_path = Path(pdf_path)

    if not pdf_path.exists():
        raise FileNotFoundError(
            f"PDF not found: {pdf_path}"
        )

    converter = DocumentConverter()

    result = converter.convert(
        str(pdf_path)
    )

    document = result.document

    markdown = document.export_to_markdown()

    if not markdown or not markdown.strip():
        raise ValueError(
            "Docling extracted an empty document."
        )

    return markdown


def extract_pdf_structure(pdf_path: str) -> dict:
    """
    Convert an arbitrary PDF and return Docling's
    structured document representation.

    This preserves richer document information than
    plain text, including document structure and tables.
    """

    pdf_path = Path(pdf_path)

    if not pdf_path.exists():
        raise FileNotFoundError(
            f"PDF not found: {pdf_path}"
        )

    converter = DocumentConverter()

    result = converter.convert(
        str(pdf_path)
    )

    document = result.document

    structure = document.export_to_dict()

    if not isinstance(structure, dict):
        raise ValueError(
            "Docling did not return a valid document structure."
        )

    return structure