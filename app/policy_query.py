import json
from pathlib import Path

from app.policy_retriever import PolicyRetriever


class PolicyQuery:

    def __init__(
        self,
        index_path: str,
        chunks_path: str,
    ):
        self.index_path = Path(index_path)
        self.chunks_path = Path(chunks_path)

        if not self.index_path.exists():
            raise FileNotFoundError(
                f"Policy index not found: {self.index_path}"
            )

        if not self.chunks_path.exists():
            raise FileNotFoundError(
                f"Policy chunks not found: {self.chunks_path}"
            )

        self.retriever = PolicyRetriever()

        with open(
            self.chunks_path,
            "r",
            encoding="utf-8"
        ) as file:
            self.chunks = json.load(file)

        self.retriever.load_index(
            str(self.index_path),
            self.chunks
        )

    def query(
        self,
        question: str,
        top_k: int = 5
    ) -> list:

        if not question.strip():
            raise ValueError(
                "Query cannot be empty."
            )

        return self.retriever.retrieve(
            question,
            top_k=top_k
        )
    def retrieve_multiple(
        self,
        queries,
        top_k=5,
        per_query_k=5
    ) -> list:

        if not queries:
            raise ValueError(
                "Queries cannot be empty."
            )

        results = self.retriever.retrieve_multiple(
            queries,
            top_k=top_k,
            per_query_k=per_query_k
        )

        unique = []
        seen = set()

        for result in results:
            key = (
                result.get("chunk_index"),
                result.get("text"),
                str(result.get("heading"))
            )

            if key not in seen:
                seen.add(key)
                unique.append(result)

        return unique[:top_k]