from dataclasses import dataclass

from app.document_chunker import chunk_policy_document


@dataclass
class DocumentProcessingPlan:
    """
    Describes how a document should be processed.

    mode:
        "full"   -> send the complete document
        "chunks" -> process structured chunks
    """

    mode: str
    document_text: str
    chunks: list


def create_processing_plan(
    document_text: str,
    max_document_characters: int = 30000,
    chunk_size: int = 1800,
    overlap: int = 250
) -> DocumentProcessingPlan:
    """
    Decide whether a document can be processed as one complete
    document or should use structured chunks.

    This function knows nothing about the policy domain or
    policy structure.
    """

    if not document_text or not document_text.strip():
        raise ValueError(
            "Document text is empty."
        )

    document_text = document_text.strip()

    # Small enough to preserve complete-document context
    if len(document_text) <= max_document_characters:

        return DocumentProcessingPlan(
            mode="full",
            document_text=document_text,
            chunks=[]
        )

    # Large document
    chunks = chunk_policy_document(
        document_text,
        chunk_size=chunk_size,
        overlap=overlap
    )

    if not chunks:
        raise ValueError(
            "Document could not be divided into chunks."
        )

    return DocumentProcessingPlan(
        mode="chunks",
        document_text=document_text,
        chunks=chunks
    )