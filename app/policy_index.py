import json
import os

import faiss

from app.document_chunker import chunk_policy_document
from app.policy_retriever import PolicyRetriever


def build_policy_index(
    document_text,
    index_path,
    chunks_path
):
    """
    Build and persist a semantic index for a policy document.

    The caller provides policy-specific output paths.
    No policy-specific assumptions are made.
    """

    chunks = chunk_policy_document(
        document_text
    )

    if not chunks:
        raise ValueError(
            "No chunks were generated."
        )

    retriever = PolicyRetriever()

    retriever.build_index(
        chunks
    )

    index_dir = os.path.dirname(index_path)
    chunks_dir = os.path.dirname(chunks_path)

    if index_dir:
        os.makedirs(
            index_dir,
            exist_ok=True
        )

    if chunks_dir:
        os.makedirs(
            chunks_dir,
            exist_ok=True
        )

    faiss.write_index(
        retriever.index,
        index_path
    )

    with open(
        chunks_path,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            chunks,
            file,
            indent=2,
            ensure_ascii=False
        )

    return retriever


def load_policy_index(
    index_path,
    chunks_path
):
    """
    Load a previously created policy index.
    """

    if not os.path.exists(
        index_path
    ):

        raise FileNotFoundError(
            f"FAISS index not found: {index_path}"
        )

    if not os.path.exists(
        chunks_path
    ):

        raise FileNotFoundError(
            f"Policy chunks not found: {chunks_path}"
        )

    index = faiss.read_index(
        index_path
    )

    with open(
        chunks_path,
        "r",
        encoding="utf-8"
    ) as file:

        chunks = json.load(
            file
        )

    retriever = PolicyRetriever()

    retriever.index = index
    retriever.chunks = chunks

    return retriever