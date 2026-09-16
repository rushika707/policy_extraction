import json

from app.policy_extractor import _extract_json_content


def test_valid_json():

    response = """
    {
        "documentInformation": {
            "title": "Example Policy"
        },
        "requirements": [
            {
                "text": "Example requirement"
            }
        ]
    }
    """

    result = _extract_json_content(
        response
    )

    assert isinstance(
        result,
        dict
    )

    assert (
        result["documentInformation"]["title"]
        == "Example Policy"
    )


def test_json_code_fence():

    response = """```json
    {
        "sections": [
            {
                "name": "Example",
                "content": "Test"
            }
        ]
    }
    ```"""

    result = _extract_json_content(
        response
    )

    assert isinstance(
        result,
        dict
    )

    assert (
        result["sections"][0]["name"]
        == "Example"
    )


def test_nested_dynamic_structure():

    response = """
    {
        "riskFramework": {
            "categories": [
                {
                    "name": "High",
                    "criteria": {
                        "threshold": 90
                    }
                }
            ]
        },
        "approvalProcess": {
            "required": true
        }
    }
    """

    result = _extract_json_content(
        response
    )

    assert (
        result["riskFramework"]
        ["categories"][0]
        ["criteria"]["threshold"]
        == 90
    )

    assert (
        result["approvalProcess"]["required"]
        is True
    )