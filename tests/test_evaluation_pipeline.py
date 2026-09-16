from app.evaluation_pipeline import EvaluationPipeline


class FakePolicyQuery:

    def query(self, query, top_k=5):
        return [
            {
                "heading": [
                    "Example Policy",
                    "Requirement"
                ],
                "text": "Example policy requirement.",
                "score": 0.9
            }
        ]


class FakeEvaluator:

    def evaluate(
        self,
        input_data,
        policy_context
    ):
        return {
            "result": "PASS",
            "reasoning": "Test evaluation.",
            "evidence": [
                {
                    "policy_section": "Requirement",
                    "policy_text": "Example policy requirement."
                }
            ]
        }


def test_evaluation_pipeline_is_generic():

    pipeline = EvaluationPipeline(
        policy_query=FakePolicyQuery(),
        evaluator=FakeEvaluator()
    )

    input_data = {
        "arbitrary_field": "arbitrary value",
        "another_field": 123
    }

    result = pipeline.evaluate(input_data)

    assert "result" in result
    assert "reason" in result

    assert result["result"] == "PASS"
    assert result["reason"] == "Test evaluation."