from app.policy_retriever import PolicyRetriever


def test_retriever_returns_results():

    chunks = [
        {
            "chunk_index": 0,
            "block_index": 0,
            "block_type": "text",
            "heading": ["Introduction"],
            "text": (
                "This document describes "
                "data handling requirements."
            )
        },
        {
            "chunk_index": 1,
            "block_index": 1,
            "block_type": "text",
            "heading": ["Security"],
            "text": (
                "Access to protected information "
                "must be controlled."
            )
        },
        {
            "chunk_index": 2,
            "block_index": 2,
            "block_type": "text",
            "heading": ["Retention"],
            "text": (
                "Records must be retained "
                "for the required period."
            )
        }
    ]

    retriever = PolicyRetriever()

    retriever.build_index(
        chunks
    )

    results = retriever.retrieve(
        "information access security",
        top_k=2
    )

    assert len(results) == 2

    assert all(
        "text" in result
        for result in results
    )

    assert all(
        "score" in result
        for result in results
    )


def test_retriever_preserves_chunk_metadata():

    chunks = [
        {
            "chunk_index": 10,
            "block_index": 5,
            "block_type": "table",
            "heading": ["Requirements"],
            "text": (
                "| Requirement | Value |\n"
                "|---|---|\n"
                "| Example | Required |"
            )
        }
    ]

    retriever = PolicyRetriever()

    retriever.build_index(
        chunks
    )

    results = retriever.retrieve(
        "requirement value",
        top_k=1
    )

    assert len(results) == 1

    result = results[0]

    assert result["chunk_index"] == 10
    assert result["block_index"] == 5
    assert result["block_type"] == "table"
    assert result["heading"] == ["Requirements"]