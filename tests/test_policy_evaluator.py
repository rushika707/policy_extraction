import json

from app.policy_evaluator import PolicyEvaluator


class FakeClient:

    def generate(
        self,
        prompt,
        temperature=0,
        max_tokens=8192
    ):
        return json.dumps({
            "overall_result": "PASS",
            "summary": "The input satisfies the supplied policy.",
            "items": [
                {
                    "input": {
                        "name": "Example",
                        "value": 42
                    },
                    "result": "PASS",
                    "reasoning": "Test evaluation.",
                    "evidence": [
                        {
                            "policy_section": "Example section",
                            "policy_text": "Example requirement."
                        }
                    ]
                }
            ]
        })


def test_policy_evaluator_is_generic():

    evaluator = PolicyEvaluator(
        client=FakeClient()
    )

    input_data = {
        "name": "Example",
        "value": 42
    }

    policy_context = [
        {
            "heading": [
                "Example Policy",
                "Requirement"
            ],
            "text": (
                "Example policy requirement."
            )
        }
    ]

    result = evaluator.evaluate(
        input_data,
        policy_context
    )

    assert isinstance(
        result,
        dict
    )

    assert "overall_result" in result

    assert "summary" in result

    assert "items" in result

    assert isinstance(
        result["items"],
        list
    )

    assert len(
        result["items"]
    ) == 1

    assert (
        result["items"][0]["result"]
        == "PASS"
    )

    assert "reasoning" in (
        result["items"][0]
    )

    assert "evidence" in (
        result["items"][0]
    )