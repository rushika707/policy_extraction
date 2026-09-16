def mock_extract_policy_chunks(chunks):
    """
    Deterministic mock extraction used only for testing
    the chunk -> fragment -> merge -> validation pipeline.

    No LLM or API call is made.
    """

    if not chunks:
        raise ValueError(
            "No document chunks were provided."
        )

    fragments = []

    for chunk in chunks:

        fragments.append({
            "chunk_index": chunk.get(
                "chunk_index"
            ),
            "block_index": chunk.get(
                "block_index"
            ),
            "block_type": chunk.get(
                "block_type"
            ),
            "heading": chunk.get(
                "heading"
            ),
            "data": chunk.get(
                "text"
            )
        })

    return fragments