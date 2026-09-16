from app.policy_extractor import (
    _extract_json_content,
    merge_policy_fragments
)


def test_extract_json_object():

    result = _extract_json_content(
        '{"name": "Example", "value": 10}'
    )

    assert isinstance(
        result,
        dict
    )

    assert result["name"] == "Example"


def test_extract_json_array():

    result = _extract_json_content(
        '[{"name": "A"}, {"name": "B"}]'
    )

    assert isinstance(
        result,
        list
    )

    assert len(result) == 2


def test_extract_json_code_fence():

    result = _extract_json_content(
        """```json
{"title": "Example"}
```"""
    )

    assert result == {
        "title": "Example"
    }


def test_merge_fragments_preserves_order():

    fragments = [
        {
            "chunk_index": 2,
            "block_index": 2,
            "block_type": "text",
            "heading": ["Second"],
            "data": {
                "content": "Second chunk"
            }
        },
        {
            "chunk_index": 0,
            "block_index": 0,
            "block_type": "text",
            "heading": ["First"],
            "data": {
                "content": "First chunk"
            }
        },
        {
            "chunk_index": 1,
            "block_index": 1,
            "block_type": "table",
            "heading": ["Table"],
            "data": {
                "rows": [
                    ["A", "B"]
                ]
            }
        }
    ]

    result = merge_policy_fragments(
        fragments
    )

    output = result[
        "documentFragments"
    ]

    assert len(output) == 3

    assert output[0][
        "chunkIndex"
    ] == 0

    assert output[1][
        "chunkIndex"
    ] == 1

    assert output[2][
        "chunkIndex"
    ] == 2


def test_merge_does_not_drop_different_structures():

    fragments = [
        {
            "chunk_index": 0,
            "block_index": 0,
            "block_type": "text",
            "heading": ["A"],
            "data": {
                "alpha": "value"
            }
        },
        {
            "chunk_index": 1,
            "block_index": 1,
            "block_type": "text",
            "heading": ["B"],
            "data": [
                {
                    "beta": "value"
                }
            ]
        }
    ]

    result = merge_policy_fragments(
        fragments
    )

    output = result[
        "documentFragments"
    ]

    assert output[0][
        "content"
    ] == {
        "alpha": "value"
    }

    assert output[1][
        "content"
    ] == [
        {
            "beta": "value"
        }
    ]