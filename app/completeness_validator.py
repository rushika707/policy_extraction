import json
import re


# ============================================================
# GENERIC STRUCTURAL VALIDATION
# ============================================================

def validate_policy_structure(
    source_text: str,
    extracted_json
):
    """
    Generic validation of an LLM-generated representation
    of an arbitrary document.

    This validator is policy-agnostic.

    It does not assume:
        - rules
        - conditions
        - actions
        - decisions
        - thresholds
        - PII
        - compliance
        - policy-specific field names
    """

    if not source_text or not source_text.strip():
        raise ValueError(
            "Source document is empty."
        )

    if extracted_json is None:
        raise ValueError(
            "Extracted JSON is null."
        )

    result = {
        "valid": True,
        "issues": [],
        "warnings": [],
        "statistics": {}
    }

    source_text = source_text.strip()

    # ========================================================
    # 1. SERIALIZATION CHECK
    # ========================================================

    try:

        serialized_json = json.dumps(
            extracted_json,
            ensure_ascii=False
        )

    except (TypeError, ValueError) as exc:

        result["valid"] = False

        result["issues"].append(
            f"Extracted result cannot be serialized as JSON: {exc}"
        )

        return result

    # ========================================================
    # 2. BASIC STATISTICS
    # ========================================================

    source_headings = _extract_headings(
        source_text
    )

    source_tables = _count_markdown_tables(
        source_text
    )

    json_statistics = _calculate_json_statistics(
        extracted_json
    )

    result["statistics"] = {
        "source_characters": len(source_text),
        "source_headings": len(source_headings),
        "source_tables": source_tables,
        "json_characters": len(serialized_json),
        **json_statistics
    }

    # ========================================================
    # 3. EMPTY EXTRACTION
    # ========================================================

    if not extracted_json:

        result["valid"] = False

        result["issues"].append(
            "Extracted JSON is empty."
        )

        return result

    # ========================================================
    # 4. SUSPICIOUS STRUCTURAL PATTERNS
    # ========================================================

    suspicious_patterns = (
        _find_suspicious_patterns(
            extracted_json
        )
    )

    if suspicious_patterns:

        # Structural corruption is a failure,
        # not merely a warning.
        result["valid"] = False

        for pattern in suspicious_patterns:

            result["issues"].append(
                pattern
            )

    # ========================================================
    # 5. HEADING COVERAGE
    # ========================================================

    missing_headings = (
        _find_missing_headings(
            source_headings,
            serialized_json
        )
    )

    result["statistics"][
        "unmatched_headings"
    ] = missing_headings

    if missing_headings:

        # A heading may legitimately be represented
        # semantically, so only fail when a substantial
        # portion of headings is missing.

        heading_count = len(
            source_headings
        )

        missing_count = len(
            missing_headings
        )

        missing_ratio = (
            missing_count / heading_count
            if heading_count
            else 0
        )

        result["statistics"][
            "heading_coverage"
        ] = round(
            1 - missing_ratio,
            3
        )

        if missing_ratio >= 0.40:

            result["valid"] = False

            result["issues"].append(
                "A substantial portion of source headings "
                "is not represented in the extracted JSON."
            )

        else:

            result["warnings"].append(
                "Some source headings were not found literally "
                "in the extracted JSON."
            )

    # ========================================================
    # 6. TEXT COVERAGE
    # ========================================================

    coverage = _estimate_text_coverage(
        source_text,
        serialized_json
    )

    result["statistics"][
        "text_coverage"
    ] = coverage

    if coverage < 0.50:

        result["valid"] = False

        result["issues"].append(
            "Extracted JSON has very low textual coverage "
            "of the source document."
        )

    elif coverage < 0.70:

        result["warnings"].append(
            "Extracted JSON has relatively low textual "
            "coverage of the source document."
        )

    # ========================================================
    # 7. DOCUMENT SIZE COMPARISON
    # ========================================================

    source_length = len(
        source_text
    )

    json_length = len(
        serialized_json
    )

    size_ratio = (
        json_length / source_length
        if source_length
        else 0
    )

    result["statistics"][
        "json_to_source_ratio"
    ] = round(
        size_ratio,
        3
    )

    if (
        source_length > 5000
        and size_ratio < 0.20
    ):

        result["warnings"].append(
            "Extracted JSON is substantially smaller than "
            "the source document and may be incomplete."
        )

    # ========================================================
    # 8. SOURCE TAIL COVERAGE
    # ========================================================

    source_tail = _meaningful_tail(
        source_text
    )

    if source_tail:

        tail_coverage = (
            _estimate_text_coverage(
                source_tail,
                serialized_json
            )
        )

        result["statistics"][
            "source_tail_coverage"
        ] = tail_coverage

        if tail_coverage < 0.30:

            result["valid"] = False

            result["issues"].append(
                "The ending portion of the source document "
                "does not appear to be represented in the "
                "extracted JSON."
            )

        elif tail_coverage < 0.50:

            result["warnings"].append(
                "The ending portion of the source document "
                "has relatively low representation."
            )

    # ========================================================
    # 9. FINAL STATUS
    # ========================================================

    return result


# ============================================================
# HEADING EXTRACTION
# ============================================================

def _extract_headings(text):

    headings = []

    for line in text.splitlines():

        line = line.strip()

        match = re.match(
            r"^#{1,6}\s+(.+?)\s*$",
            line
        )

        if match:

            heading = match.group(1).strip()

            if heading:
                headings.append(
                    heading
                )

    return headings


# ============================================================
# TABLE COUNT
# ============================================================

def _count_markdown_tables(text):

    lines = text.splitlines()

    count = 0
    index = 0

    while index + 1 < len(lines):

        current = lines[index].strip()
        next_line = lines[index + 1].strip()

        if (
            "|" in current
            and _is_table_separator(next_line)
        ):

            count += 1

            index += 2

            while (
                index < len(lines)
                and "|" in lines[index]
            ):

                index += 1

            continue

        index += 1

    return count


def _is_table_separator(line):

    return re.match(
        r"^\s*\|?\s*:?-+:?\s*(\|\s*:?-+:?\s*)+\|?\s*$",
        line
    ) is not None


# ============================================================
# JSON STATISTICS
# ============================================================

def _calculate_json_statistics(value):

    statistics = {
        "objects": 0,
        "arrays": 0,
        "strings": 0,
        "numbers": 0,
        "booleans": 0,
        "nulls": 0,
        "keys": 0
    }

    def walk(node):

        if isinstance(node, dict):

            statistics["objects"] += 1

            statistics["keys"] += len(
                node
            )

            for key, child in node.items():

                if isinstance(key, str):
                    statistics["strings"] += 1

                walk(child)

        elif isinstance(node, list):

            statistics["arrays"] += 1

            for child in node:
                walk(child)

        elif isinstance(node, str):

            statistics["strings"] += 1

        elif isinstance(node, bool):

            statistics["booleans"] += 1

        elif isinstance(node, (int, float)):

            statistics["numbers"] += 1

        elif node is None:

            statistics["nulls"] += 1

    walk(value)

    return statistics


# ============================================================
# SUSPICIOUS STRUCTURE DETECTION
# ============================================================

def _find_suspicious_patterns(value):

    serialized = json.dumps(
        value,
        ensure_ascii=False
    )

    problems = []

    # --------------------------------------------------------
    # Literal ":" values
    # --------------------------------------------------------

    literal_colon_values = re.findall(
        r':\s*"([^"]*)"',
        serialized
    )

    colon_count = literal_colon_values.count(
        ":"
    )

    if colon_count >= 2:

        problems.append(
            "Extracted JSON contains multiple literal ':' "
            "values, which may indicate that JSON object "
            "syntax was incorrectly represented as data."
        )

    # --------------------------------------------------------
    # Arrays containing alternating key / ":" / value
    # --------------------------------------------------------

    if isinstance(value, list):

        for item in value:

            if isinstance(item, list):

                if _looks_like_key_value_token_list(
                    item
                ):

                    problems.append(
                        "Extracted JSON contains an array "
                        "that appears to represent object "
                        "syntax as separate tokens."
                    )

            elif isinstance(item, dict):

                nested_problems = (
                    _find_suspicious_patterns(
                        item
                    )
                )

                problems.extend(
                    nested_problems
                )

    # --------------------------------------------------------
    # Recursive dictionary inspection
    # --------------------------------------------------------

    if isinstance(value, dict):

        for child in value.values():

            if isinstance(
                child,
                (dict, list)
            ):

                problems.extend(
                    _find_suspicious_patterns(
                        child
                    )
                )

    return list(
        dict.fromkeys(
            problems
        )
    )


def _looks_like_key_value_token_list(
    value
):

    if len(value) < 3:
        return False

    colon_positions = [
        index
        for index, item in enumerate(value)
        if item == ":"
    ]

    if not colon_positions:
        return False

    return True


# ============================================================
# HEADING COVERAGE
# ============================================================

def _find_missing_headings(
    headings,
    serialized_json
):

    normalized_json = _normalize_text(
        serialized_json
    )

    missing = []

    for heading in headings:

        normalized_heading = (
            _normalize_text(
                heading
            )
        )

        if (
            normalized_heading
            and normalized_heading
            not in normalized_json
        ):

            missing.append(
                heading
            )

    return missing


# ============================================================
# TEXT COVERAGE
# ============================================================

def _estimate_text_coverage(
    source_text,
    extracted_text
):

    source_tokens = _meaningful_tokens(
        source_text
    )

    if not source_tokens:
        return 1.0

    extracted_tokens = set(
        _meaningful_tokens(
            extracted_text
        )
    )

    matched = sum(
        1
        for token in source_tokens
        if token in extracted_tokens
    )

    return round(
        matched / len(source_tokens),
        3
    )


def _meaningful_tokens(text):

    tokens = re.findall(
        r"[A-Za-z0-9][A-Za-z0-9_./@+-]{2,}",
        text.lower()
    )

    stop_tokens = {
        "the",
        "and",
        "for",
        "that",
        "this",
        "with",
        "from",
        "are",
        "was",
        "were",
        "has",
        "have",
        "into",
        "used",
        "must",
        "shall",
        "may",
        "can",
        "not",
        "all",
        "any"
    }

    return [
        token
        for token in tokens
        if token not in stop_tokens
    ]


# ============================================================
# NORMALIZATION
# ============================================================

def _normalize_text(text):

    return re.sub(
        r"\s+",
        " ",
        text.lower()
    ).strip()


# ============================================================
# SOURCE TAIL
# ============================================================

def _meaningful_tail(
    text,
    characters=2000
):

    if len(text) <= characters:

        tail = text

    else:

        tail = text[-characters:]

    return tail.strip()