from app.document_chunker import chunk_policy_document


def test_table_is_kept_together():

    document = """
# Example Policy

## Requirements

| ID | Requirement | Outcome |
|---|---|---|
| R1 | Requirement one | PASS |
| R2 | Requirement two | FLAG |
| R3 | Requirement three | BLOCK |
| R4 | Requirement four | REVIEW |
"""

    chunks = chunk_policy_document(
        document,
        chunk_size=50
    )

    table_chunks = [
        chunk
        for chunk in chunks
        if chunk["block_type"] == "table"
    ]

    assert len(table_chunks) == 1

    table = table_chunks[0]["text"]

    assert "R1" in table
    assert "R2" in table
    assert "R3" in table
    assert "R4" in table


def test_heading_context_is_preserved():

    document = """
# Main Policy

## Data Requirements

This is a requirement.

### Special Cases

This is a special case.
"""

    chunks = chunk_policy_document(
        document
    )

    headings = [
        chunk["heading"]
        for chunk in chunks
    ]

    assert [
        "Main Policy",
        "Data Requirements"
    ] in headings

    assert [
        "Main Policy",
        "Data Requirements",
        "Special Cases"
    ] in headings


def test_normal_text_can_be_chunked():

    document = """
# Policy

This is the first paragraph.

This is the second paragraph.

This is the third paragraph.
"""

    chunks = chunk_policy_document(
        document,
        chunk_size=60
    )

    assert len(chunks) > 1

    for chunk in chunks:
        assert chunk["text"].strip()


def test_empty_document():

    chunks = chunk_policy_document("")

    assert chunks == []


def test_table_is_identified_as_table():

    document = """
# Policy

| Field | Description |
|---|---|
| A | First |
| B | Second |
"""

    chunks = chunk_policy_document(
        document
    )

    assert len(chunks) == 1

    assert chunks[0]["block_type"] == "table"