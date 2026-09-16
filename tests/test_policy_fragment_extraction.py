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
            "data": {"content": "Second chunk"}
        },
        {
            "chunk_index": 0,
            "data": {"content": "First chunk"}
        },
        {
            "chunk_index": 1,
            "data": {"rows": [["A", "B"]]}
        }
    ]

    result = merge_policy_fragments(fragments)

    output = result["policies"]

    assert output[0]["content"] == "First chunk"
    assert output[1]["rows"] == [["A", "B"]]
    assert output[2]["content"] == "Second chunk"


def test_merge_does_not_drop_different_structures():
    fragments = [
        {
            "chunk_index": 0,
            "data": {"alpha": "value"}
        },
        {
            "chunk_index": 1,
            "data": [{"beta": "value"}]
        }
    ]

    result = merge_policy_fragments(fragments)

    output = result["policies"]

    assert output[0] == {"alpha": "value"}
    assert output[1] == [{"beta": "value"}]