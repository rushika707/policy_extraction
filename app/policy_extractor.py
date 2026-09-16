import json
import os

from groq import Groq


PROMPT_PATH = "prompts/policy_extraction.txt"


# ============================================================
# PROMPT
# ============================================================

def _load_prompt():
    """Load the generic document extraction prompt."""

    if not os.path.exists(PROMPT_PATH):
        raise FileNotFoundError(
            f"Prompt file not found: {PROMPT_PATH}"
        )

    with open(
        PROMPT_PATH,
        "r",
        encoding="utf-8"
    ) as file:

        return file.read()


# ============================================================
# JSON PARSING
# ============================================================

def _extract_json_content(response_text):
    """
    Parse JSON returned by the LLM.

    The root structure is intentionally dynamic.
    """

    if not response_text:
        raise ValueError(
            "LLM returned an empty response."
        )

    response_text = response_text.strip()

    # Handle accidental Markdown code fences.
    if response_text.startswith("```"):

        lines = response_text.splitlines()

        if lines:
            lines = lines[1:]

        if (
            lines
            and lines[-1].strip() == "```"
        ):
            lines = lines[:-1]

        response_text = "\n".join(
            lines
        ).strip()

    try:

        return json.loads(
            response_text
        )

    except json.JSONDecodeError as exc:

        raise ValueError(
            "LLM response was not valid JSON."
        ) from exc


# ============================================================
# GROQ CLIENT
# ============================================================

def _create_client():

    api_key = os.getenv(
        "GROQ_API_KEY"
    )

    if not api_key:

        raise ValueError(
            "GROQ_API_KEY is not configured."
        )

    return Groq(
        api_key=api_key
    )


def _get_model():

    return os.getenv(
        "GROQ_MODEL",
        "openai/gpt-oss-20b"
    )


# ============================================================
# DYNAMIC BATCHING
# ============================================================

def create_dynamic_batches(
    chunks,
    max_input_tokens=6000
):
    """
    Dynamically group document chunks according to an
    estimated input-token budget.

    This function is completely policy-agnostic.

    It does not know:
        - policy type
        - rule types
        - fields
        - conditions
        - actions
        - decisions
        - thresholds
        - exceptions

    It only considers the size of the supplied chunks.
    """

    if not chunks:

        raise ValueError(
            "No document chunks were provided."
        )

    batches = []

    current_batch = []

    current_tokens = 0

    for chunk in chunks:

        text = chunk.get(
            "text",
            ""
        )

        if not text:
            continue

        # Approximate token count.
        #
        # Rough estimate:
        # 4 characters ≈ 1 token
        #
        # This is deliberately conservative enough
        # for batching purposes.
        estimated_tokens = max(
            1,
            len(text) // 4
        )

        # If adding the next chunk would exceed the
        # current batch budget, finalize the current batch.
        if (
            current_batch
            and
            current_tokens + estimated_tokens
            > max_input_tokens
        ):

            batches.append(
                current_batch
            )

            current_batch = []

            current_tokens = 0

        current_batch.append(
            chunk
        )

        current_tokens += estimated_tokens

    # Add final batch.
    if current_batch:

        batches.append(
            current_batch
        )

    return batches


# ============================================================
# FULL DOCUMENT EXTRACTION
# ============================================================

def extract_policy(
    document_text: str,
    client=None
):
    """
    Extract a complete document using one Groq call.

    This function is retained for compatibility.

    The main pipeline should use
    extract_policy_chunks(), which performs
    dynamic batching.
    """

    if not document_text or not document_text.strip():

        raise ValueError(
            "Document text is empty."
        )

    if client is None:

        client = _create_client()

    instructions = _load_prompt()

    model = _get_model()

    response = client.chat.completions.create(

        model=model,

        messages=[
            {
                "role": "system",
                "content": instructions
            },
            {
                "role": "user",
                "content": (
                    "Analyse the following complete "
                    "document and return its dynamic "
                    "JSON representation.\n\n"
                    "Do not invent information.\n"
                    "Preserve the document's structure "
                    "and all meaningful information.\n\n"
                    "DOCUMENT:\n"
                    + document_text
                )
            }
        ],

        temperature=0,

        response_format={
            "type": "json_object"
        }
    )

    response_text = (
        response
        .choices[0]
        .message
        .content
    )

    _save_raw_response(
        response_text,
        "output/raw_groq_response.txt"
    )

    return _extract_json_content(
        response_text
    )


# ============================================================
# DYNAMIC CHUNK EXTRACTION
# ============================================================

def extract_policy_chunks(
    chunks,
    client=None
):
    """
    Extract document chunks using dynamically sized
    Groq batches.

    The batching mechanism is independent of policy
    semantics.

    Each source chunk is preserved using its original
    chunk_index.
    """

    if not chunks:

        raise ValueError(
            "No document chunks were provided."
        )

    if client is None:

        client = _create_client()

    instructions = _load_prompt()

    model = _get_model()

    # --------------------------------------------------------
    # Create dynamic batches
    # --------------------------------------------------------

    batches = create_dynamic_batches(
        chunks,
        max_input_tokens=6000
    )

    print(
        f"Created {len(batches)} "
        f"dynamic Groq batches."
    )

    fragments = []

    # --------------------------------------------------------
    # Process each dynamic batch
    # --------------------------------------------------------

    for batch_number, batch in enumerate(
        batches,
        start=1
    ):

        print()
        print(
            f"Processing Groq batch "
            f"{batch_number}/{len(batches)}"
        )

        chunk_payload = []

        for chunk in batch:

            chunk_index = chunk.get(
                "chunk_index"
            )

            chunk_text = chunk.get(
                "text"
            )

            if not chunk_text:
                continue

            chunk_payload.append({
                "chunk_index": chunk_index,

                "block_index": chunk.get(
                    "block_index"
                ),

                "block_type": chunk.get(
                    "block_type"
                ),

                "heading": chunk.get(
                    "heading"
                ),

                "text": chunk_text
            })

        if not chunk_payload:

            continue

        # ----------------------------------------------------
        # Serialize chunks
        # ----------------------------------------------------

        serialized_chunks = json.dumps(
            chunk_payload,
            ensure_ascii=False,
            indent=2
        )

        # ----------------------------------------------------
        # Generic extraction prompt
        # ----------------------------------------------------

        user_prompt = f"""
Extract the information from EVERY document chunk
provided below.

Return ONLY a valid JSON object with this structure:

{{
  "fragments": [
    {{
      "chunk_index": <original chunk index>,
      "content": <dynamic JSON representation of that chunk>
    }}
  ]
}}

IMPORTANT:

1. Create exactly one fragment for every supplied chunk.

2. Preserve the original chunk_index exactly.

3. The "content" must be dynamically derived from
   the supplied document content.

4. Do NOT use a predefined universal policy schema.

5. Do NOT assume concepts such as:
   - rule_type
   - conditions
   - actions
   - decisions
   - thresholds
   - exceptions
   - controls

   unless those concepts actually appear in the
   supplied document.

6. Preserve tables, headings, identifiers, labels,
   requirements, statements, classifications,
   criteria, relationships, exceptions, outcomes,
   responsibilities, dates, values and other
   meaningful information when present.

7. Preserve relationships explicitly represented
   inside the source chunk.

8. Do not invent information.

9. Do not merge information from different chunks.

10. Do not omit meaningful information merely to make
    the JSON smaller.

11. The resulting JSON will be used as the source of
    truth for downstream policy processing.

DOCUMENT CHUNKS:

{serialized_chunks}
"""

        # ----------------------------------------------------
        # Groq request
        # ----------------------------------------------------

        response = client.chat.completions.create(

            model=model,

            messages=[
                {
                    "role": "system",
                    "content": instructions
                },
                {
                    "role": "user",
                    "content": user_prompt
                }
            
            ],

            temperature=0,
            max_completion_tokens=8192,
            reasoning_effort="low",
            include_reasoning=False
        )

        message = response.choices[0].message

        print()
        print("GROQ MESSAGE:")
        print(message)

        print()
        print("FINISH REASON:")
        print(
            response.choices[0].finish_reason
        )

        print()
        print("USAGE:")
        print(
            response.usage
        )

        response_text = (
            message.content
        )
        print()
        print("RAW GROQ RESPONSE:")
        print(response_text)
        print()

        # ----------------------------------------------------
        # Parse response
        # ----------------------------------------------------

        batch_result = _extract_json_content(
            response_text
        )

        if not isinstance(
            batch_result,
            dict
        ):

            raise ValueError(
                "Groq batch response must be "
                "a JSON object."
            )

        batch_fragments = batch_result.get(
            "fragments"
        )

        if not isinstance(
            batch_fragments,
            list
        ):

            raise ValueError(
                "Groq batch response does not "
                "contain a valid 'fragments' array."
            )

        # ----------------------------------------------------
        # Validate returned chunk indexes
        # ----------------------------------------------------

        expected_indices = {
            item["chunk_index"]
            for item in chunk_payload
        }

        returned_indices = set()

        for fragment in batch_fragments:

            if not isinstance(
                fragment,
                dict
            ):

                raise ValueError(
                    "Each returned fragment must "
                    "be a JSON object."
                )

            chunk_index = fragment.get(
                "chunk_index"
            )

            if chunk_index not in expected_indices:

                raise ValueError(
                    "Groq returned an unknown "
                    f"chunk_index: {chunk_index}"
                )

            if chunk_index in returned_indices:

                raise ValueError(
                    "Groq returned duplicate "
                    f"chunk_index: {chunk_index}"
                )

            returned_indices.add(
                chunk_index
            )

        # ----------------------------------------------------
        # Check for missing chunks
        # ----------------------------------------------------

        missing_indices = (
            expected_indices
            - returned_indices
        )

        if missing_indices:

            raise ValueError(
                "Groq failed to return fragments "
                "for chunks: "
                f"{sorted(missing_indices)}"
            )

        # ----------------------------------------------------
        # Attach original source metadata
        # ----------------------------------------------------

        source_chunks = {
            item["chunk_index"]: item
            for item in chunk_payload
        }

        for fragment in batch_fragments:

            chunk_index = fragment[
                "chunk_index"
            ]

            source_chunk = source_chunks[
                chunk_index
            ]

            fragments.append({
                "chunk_index": chunk_index,

                "block_index": source_chunk.get(
                    "block_index"
                ),

                "block_type": source_chunk.get(
                    "block_type"
                ),

                "heading": source_chunk.get(
                    "heading"
                ),

                "data": fragment.get(
                    "content"
                )
            })

        print(
            f"Received "
            f"{len(batch_fragments)} fragments."
        )

    # --------------------------------------------------------
    # Final ordering
    # --------------------------------------------------------

    fragments.sort(
        key=lambda item: (
            item.get(
                "chunk_index",
                0
            )
        )
    )

    return fragments


# ============================================================
# GENERIC FRAGMENT MERGING
# ============================================================

def merge_policy_fragments(
    fragments
):
    """
    Merge independently extracted JSON fragments.

    This function does NOT understand the policy.

    It simply preserves every extracted fragment in
    source order.
    """

    if not fragments:

        raise ValueError(
            "No fragments were provided."
        )

    ordered_fragments = sorted(
        fragments,
        key=lambda item: (
            item.get(
                "chunk_index",
                0
            )
        )
    )

    return {
        "documentFragments": [
            {
                "chunkIndex": fragment.get(
                    "chunk_index"
                ),

                "blockIndex": fragment.get(
                    "block_index"
                ),

                "blockType": fragment.get(
                    "block_type"
                ),

                "heading": fragment.get(
                    "heading"
                ),

                "content": fragment.get(
                    "data"
                )
            }

            for fragment in ordered_fragments
        ]
    }


# ============================================================
# RAW RESPONSE STORAGE
# ============================================================

def _save_raw_response(
    response_text,
    path
):

    directory = os.path.dirname(
        path
    )

    if directory:

        os.makedirs(
            directory,
            exist_ok=True
        )

    with open(
        path,
        "w",
        encoding="utf-8"
    ) as file:

        file.write(
            response_text or ""
        )