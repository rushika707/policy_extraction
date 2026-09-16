import json
from pathlib import Path

from app.policy_query import PolicyQuery
from app.policy_evaluator import PolicyEvaluator


class EvaluationPipeline:

    def __init__(
        self,
        index_path=None,
        chunks_path=None,
        policy_query=None,
        evaluator=None
    ):
        if policy_query is not None:
            self.policy_query = policy_query
        else:
            if index_path is None or chunks_path is None:
                raise ValueError(
                    "index_path and chunks_path are required "
                    "when policy_query is not provided."
                )

            self.policy_query = PolicyQuery(
                index_path=index_path,
                chunks_path=chunks_path
            )

        self.evaluator = evaluator or PolicyEvaluator()

    def load_input_data(self, input_path):
        path = Path(input_path)

        if not path.exists():
            raise FileNotFoundError(
                f"Input file not found: {path}"
            )

        with open(path, "r", encoding="utf-8") as file:
            return json.load(file)

    def evaluate(self, input_data, top_k=15):

        if self._is_collection(input_data):

            items = []

            for item in input_data:

                policy_context = self._retrieve_for_item(
                    item,
                    top_k=top_k
                )

                evaluation = self.evaluator.evaluate(
                    input_data=item,
                    policy_context=policy_context
                )

                items.append(
                    self._clean_evaluation(
                        item,
                        evaluation
                    )
                )

            return items

        policy_context = self._retrieve_for_item(
            input_data,
            top_k=top_k
        )

        evaluation = self.evaluator.evaluate(
            input_data=input_data,
            policy_context=policy_context
        )

        return self._clean_evaluation(
            input_data,
            evaluation
        )

    def _clean_evaluation(self, input_data, evaluation):
        """Create the compact user-facing evaluation result."""

        if not isinstance(evaluation, dict):
            raise ValueError(
                "Evaluator must return a JSON object."
            )

        record_id = None

        if isinstance(input_data, dict):
            record_id = (
                input_data.get("record_id")
                or input_data.get("request_id")
                or input_data.get("expense_id")
                or input_data.get("id")
            )

        result = evaluation.get("result")

        reason = (
            evaluation.get("reasoning")
            or evaluation.get("reason")
            or ""
        )

        cleaned = {}

        if record_id is not None:
            cleaned["record_id"] = record_id

        cleaned["result"] = result
        cleaned["reason"] = reason

        return cleaned

    def _is_collection(self, input_data):
        return isinstance(input_data, list)

    def _retrieve_for_item(self, item, top_k=15):
        queries = self._build_queries(item)

        if hasattr(self.policy_query, "retrieve_multiple"):
            return self.policy_query.retrieve_multiple(
                queries,
                top_k=top_k,
                per_query_k=5
            )

        policy_context = []

        for query in queries:
            policy_context.extend(
                self.policy_query.query(
                    query,
                    top_k=top_k
                )
            )

        return policy_context

    def _build_queries(self, input_data):
        """Build generic retrieval queries from arbitrary JSON."""

        queries = []

        def add_query(value):
            if value is None:
                return

            text = str(value).strip()

            if text:
                queries.append(text)

        def walk(value, parent_key=None):

            if isinstance(value, dict):

                for key, child in value.items():

                    add_query(key)

                    if isinstance(
                        child,
                        (str, int, float, bool)
                    ):
                        add_query(
                            f"{key} {child}"
                        )

                    walk(child, key)

            elif isinstance(value, list):

                for item in value:
                    walk(item, parent_key)

            else:
                add_query(value)

        walk(input_data)

        add_query(
            json.dumps(
                input_data,
                ensure_ascii=False,
                sort_keys=True
            )
        )

        unique_queries = []
        seen = set()

        for query in queries:

            normalized = query.lower().strip()

            if normalized not in seen:
                seen.add(normalized)
                unique_queries.append(query)

        return unique_queries

    def evaluate_file(
        self,
        input_path,
        output_path=None,
        top_k=15
    ):
        input_data = self.load_input_data(input_path)

        results = self.evaluate(
            input_data,
            top_k=top_k
        )

        if output_path is not None:

            output = Path(output_path)

            output.parent.mkdir(
                parents=True,
                exist_ok=True
            )

            with open(
                output,
                "w",
                encoding="utf-8"
            ) as file:

                json.dump(
                    results,
                    file,
                    indent=2,
                    ensure_ascii=False
                )

        return results
