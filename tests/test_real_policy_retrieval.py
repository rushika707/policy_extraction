from pathlib import Path

from app.document_chunker import chunk_policy_document
from app.policy_retriever import PolicyRetriever


OUTPUT_DIR = Path("output")


def test_real_policy_retrieval():

    document_paths = list(
        OUTPUT_DIR.glob("*/document.md")
    )

    assert document_paths, (
        "No policy document found. "
        "Run `python run.py` first."
    )

    for document_path in document_paths:

        document = document_path.read_text(
            encoding="utf-8"
        )

        chunks = chunk_policy_document(
            document
        )

        assert len(chunks) > 0

        retriever = PolicyRetriever()

        retriever.build_index(
            chunks
        )

        results = retriever.retrieve(
            "mandatory requirements",
            top_k=5
        )

        assert len(results) > 0

        for result in results:

            print(
                "\n"
                + "=" * 60
            )

            print(
                "Policy:",
                document_path
            )

            print(
                "Score:",
                result["score"]
            )

            print(
                "Heading:",
                result["heading"]
            )

            print(
                result["text"]
            )