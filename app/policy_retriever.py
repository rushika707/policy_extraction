import json
import re
from pathlib import Path

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer


class PolicyRetriever:

    def __init__(
        self,
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    ):
        self.model = SentenceTransformer(model_name)
        self.index = None
        self.chunks = []

    def _chunk_text(self, chunk):
        parts = []

        heading = chunk.get("heading")

        if heading:
            if isinstance(heading, list):
                parts.extend(
                    str(item)
                    for item in heading
                    if item
                )
            else:
                parts.append(str(heading))

        section = chunk.get("section")

        if section:
            parts.append(str(section))

        text = chunk.get("text")

        if text:
            parts.append(str(text))

        return " ".join(parts)

    def build_index(self, chunks):

        self.chunks = chunks

        texts = [
            self._chunk_text(chunk)
            for chunk in chunks
        ]

        embeddings = self.model.encode(
            texts,
            convert_to_numpy=True,
            normalize_embeddings=True
        )

        embeddings = embeddings.astype(np.float32)

        dimension = embeddings.shape[1]

        self.index = faiss.IndexFlatIP(dimension)

        self.index.add(embeddings)

    def save_index(self, index_path, chunks_path):

        if self.index is None:
            raise ValueError(
                "Index has not been built."
            )

        faiss.write_index(
            self.index,
            str(index_path)
        )

        with open(
            chunks_path,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                self.chunks,
                file,
                indent=2,
                ensure_ascii=False
            )

    def load_index(
        self,
        index_path,
        chunks
    ):

        self.index = faiss.read_index(
            str(index_path)
        )

        self.chunks = chunks

    # ---------------------------------------------------------
    # Generic lexical matching
    # ---------------------------------------------------------

    def _tokenize(self, text):

        return re.findall(
            r"\b[a-zA-Z0-9][a-zA-Z0-9_-]*\b",
            text.lower()
        )

    def _lexical_score(
        self,
        query,
        chunk
    ):

        query_tokens = self._tokenize(query)

        chunk_text = self._chunk_text(chunk)

        chunk_tokens = self._tokenize(chunk_text)

        if not query_tokens or not chunk_tokens:
            return 0.0

        query_set = set(query_tokens)
        chunk_set = set(chunk_tokens)

        exact_overlap = (
            query_set & chunk_set
        )

        token_score = (
            len(exact_overlap)
            / len(query_set)
        )

        # Phrase matching
        normalized_query = " ".join(
            query_tokens
        )

        normalized_chunk = " ".join(
            chunk_tokens
        )

        phrase_score = 0.0

        if normalized_query in normalized_chunk:
            phrase_score = 1.0

        # Multi-word phrase matching
        query_phrases = []

        for size in (3, 2):
            if len(query_tokens) >= size:
                for i in range(
                    len(query_tokens) - size + 1
                ):
                    query_phrases.append(
                        " ".join(
                            query_tokens[
                                i:i + size
                            ]
                        )
                    )

        matched_phrases = sum(
            phrase in normalized_chunk
            for phrase in query_phrases
        )

        phrase_component = 0.0

        if query_phrases:
            phrase_component = (
                matched_phrases
                / len(query_phrases)
            )

        return min(
            1.0,
            0.65 * token_score
            + 0.20 * phrase_score
            + 0.15 * phrase_component
        )

    # ---------------------------------------------------------
    # Heading matching
    # ---------------------------------------------------------

    def _heading_score(
        self,
        query,
        chunk
    ):

        heading = chunk.get(
            "heading",
            []
        )

        if isinstance(heading, list):
            heading_text = " ".join(
                str(item)
                for item in heading
                if item
            )
        else:
            heading_text = str(heading)

        if not heading_text:
            return 0.0

        query_tokens = set(
            self._tokenize(query)
        )

        heading_tokens = set(
            self._tokenize(heading_text)
        )

        if not query_tokens:
            return 0.0

        overlap = (
            query_tokens
            & heading_tokens
        )

        return (
            len(overlap)
            / len(query_tokens)
        )

    # ---------------------------------------------------------
    # Retrieval
    # ---------------------------------------------------------

    def retrieve(
        self,
        query,
        top_k=5
    ):

        if self.index is None:
            raise ValueError(
                "Index has not been built."
            )

        if not query.strip():
            raise ValueError(
                "Query cannot be empty."
            )

        if top_k <= 0:
            raise ValueError(
                "top_k must be greater than zero."
            )

        candidate_k = min(
            max(top_k * 3, 10),
            len(self.chunks)
        )

        query_embedding = self.model.encode(
            [query],
            convert_to_numpy=True,
            normalize_embeddings=True
        )

        query_embedding = (
            query_embedding.astype(np.float32)
        )

        scores, indices = self.index.search(
            query_embedding,
            candidate_k
        )

        candidates = []

        for semantic_score, index in zip(
            scores[0],
            indices[0]
        ):

            if index < 0:
                continue

            chunk = self.chunks[index]

            lexical_score = (
                self._lexical_score(
                    query,
                    chunk
                )
            )

            heading_score = (
                self._heading_score(
                    query,
                    chunk
                )
            )

            # Hybrid retrieval
            final_score = (
                0.60 * float(semantic_score)
                + 0.30 * lexical_score
                + 0.10 * heading_score
            )

            result = dict(chunk)

            result["score"] = final_score

            result["semantic_score"] = (
                float(semantic_score)
            )

            result["lexical_score"] = (
                lexical_score
            )

            result["heading_score"] = (
                heading_score
            )

            candidates.append(result)

        candidates.sort(
            key=lambda item: item["score"],
            reverse=True
        )

        return candidates[:top_k]
    def retrieve_multiple(
        self,
        queries,
        top_k=5,
        per_query_k=5
    ):
        """
        Generic multi-query retrieval.

        Retrieves policy context independently for each query,
        then merges and deduplicates the results.

        No policy-specific rules or keywords are used.
        """

        if not queries:
            raise ValueError("Queries cannot be empty.")

        if top_k <= 0:
            raise ValueError(
                "top_k must be greater than zero."
            )

        if per_query_k <= 0:
            raise ValueError(
                "per_query_k must be greater than zero."
            )

        merged = {}

        for query in queries:

            if not isinstance(query, str):
                continue

            query = query.strip()

            if not query:
                continue

            results = self.retrieve(
                query,
                top_k=per_query_k
            )

            for result in results:

                chunk_index = result.get(
                    "chunk_index"
                )

                if chunk_index is None:
                    chunk_index = result.get(
                        "index"
                    )

                if chunk_index is None:
                    chunk_index = id(result)

                if chunk_index not in merged:
                    merged[chunk_index] = dict(result)

                else:
                    existing = merged[chunk_index]

                    existing["score"] = max(
                        existing.get("score", 0.0),
                        result.get("score", 0.0)
                    )

        results = list(
            merged.values()
        )

        results.sort(
            key=lambda item: item.get(
                "score",
                0.0
            ),
            reverse=True
        )

        return results[:top_k]