from app.document_processor import (
    create_processing_plan
)


def test_small_document_uses_full_mode():

    document = """
    # Example Policy

    This is a small policy document.

    It contains some requirements and
    general information.
    """

    plan = create_processing_plan(
        document,
        max_document_characters=1000
    )

    assert plan.mode == "full"

    assert plan.document_text == document.strip()

    assert plan.chunks == []


def test_large_document_uses_chunk_mode():

    document = """
    # Example Policy

    This is a paragraph containing
    some policy information.
    """ * 100

    plan = create_processing_plan(
        document,
        max_document_characters=500
    )

    assert plan.mode == "chunks"

    assert len(plan.chunks) > 0


def test_large_document_preserves_generic_headings():

    document = """
    # Governance Policy

    ## Approval

    Approval information.

    ## Monitoring

    Monitoring information.

    ## Escalation

    Escalation information.
    """ * 20

    plan = create_processing_plan(
        document,
        max_document_characters=500
    )

    assert plan.mode == "chunks"

    all_chunk_text = "\n".join(
        chunk["text"]
        for chunk in plan.chunks
    )

    assert "Approval" in all_chunk_text
    assert "Monitoring" in all_chunk_text
    assert "Escalation" in all_chunk_text


def test_table_relationships_are_preserved():

    document = """
    # Example

    ## Requirements

    | Identifier | Requirement | Outcome |
    |---|---|---|
    | A1 | Requirement A | Approve |
    | B1 | Requirement B | Review |
    | C1 | Requirement C | Reject |
    """

    plan = create_processing_plan(
        document,
        max_document_characters=100
    )

    assert plan.mode == "chunks"

    table_chunks = [
        chunk
        for chunk in plan.chunks
        if chunk["block_type"] == "table"
    ]

    assert len(table_chunks) == 1

    table = table_chunks[0]["text"]

    assert "A1" in table
    assert "Requirement A" in table
    assert "Approve" in table

    assert "B1" in table
    assert "Requirement B" in table
    assert "Review" in table

    assert "C1" in table
    assert "Requirement C" in table
    assert "Reject" in table