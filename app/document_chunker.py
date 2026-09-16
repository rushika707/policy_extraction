import re


def chunk_policy_document(
    text: str,
    chunk_size: int = 1800,
    overlap: int = 250
):
    """
    Generic Markdown-aware document chunker.

    No assumptions are made about:
    - policy domain
    - rule types
    - conditions
    - decisions
    - field names
    - policy schema

    Tables are treated as atomic blocks and are never split
    row-by-row.
    """

    if not text or not text.strip():
        return []

    lines = text.splitlines()

    blocks = []
    current_block = []
    current_heading = []

    def flush_block():
        nonlocal current_block

        if not current_block:
            return

        content = "\n".join(
            current_block
        ).strip()

        if content:
            blocks.append({
                "type": "text",
                "heading": current_heading.copy(),
                "text": content
            })

        current_block = []

    def is_heading(line):
        return re.match(
            r"^#{1,6}\s+",
            line
        ) is not None

    def is_table_start(index):
        if index + 1 >= len(lines):
            return False

        header = lines[index]
        separator = lines[index + 1]

        if "|" not in header:
            return False

        return re.match(
            r"^\s*\|?\s*:?-+:?\s*(\|\s*:?-+:?\s*)+\|?\s*$",
            separator
        ) is not None

    i = 0

    while i < len(lines):

        line = lines[i].rstrip()

        # --------------------------------------------------
        # Heading
        # --------------------------------------------------

        if is_heading(line):

            flush_block()

            level = len(
                line
            ) - len(
                line.lstrip("#")
            )

            heading_text = line[
                level:
            ].strip()

            if level <= len(
                current_heading
            ):
                current_heading = (
                    current_heading[
                        :level - 1
                    ]
                )

            current_heading.append(
                heading_text
            )

            i += 1
            continue

        # --------------------------------------------------
        # Table
        # --------------------------------------------------

        if is_table_start(i):

            flush_block()

            table_lines = [
                lines[i].rstrip(),
                lines[i + 1].rstrip()
            ]

            i += 2

            while i < len(lines):

                table_line = lines[
                    i
                ].rstrip()

                if "|" not in table_line:
                    break

                table_lines.append(
                    table_line
                )

                i += 1

            blocks.append({
                "type": "table",
                "heading": current_heading.copy(),
                "text": "\n".join(
                    table_lines
                ).strip()
            })

            continue

        # --------------------------------------------------
        # Blank line
        # --------------------------------------------------

        if not line.strip():

            flush_block()

            i += 1
            continue

        # --------------------------------------------------
        # Normal text
        # --------------------------------------------------

        current_block.append(
            line
        )

        i += 1

    flush_block()

    # ======================================================
    # Convert blocks into chunks
    # ======================================================

    chunks = []

    for block_index, block in enumerate(
        blocks
    ):

        heading = block[
            "heading"
        ]

        content = block[
            "text"
        ]

        heading_prefix = ""

        if heading:

            heading_prefix = (
                "Section: "
                + " > ".join(
                    heading
                )
                + "\n\n"
            )

        full_text = (
            heading_prefix
            + content
        ).strip()

        # --------------------------------------------------
        # Tables are ALWAYS kept intact
        # --------------------------------------------------

        if block["type"] == "table":

            chunks.append({
                "chunk_index": len(
                    chunks
                ),
                "block_index": block_index,
                "block_type": "table",
                "heading": heading,
                "text": full_text
            })

            continue

        # --------------------------------------------------
        # Normal block fits
        # --------------------------------------------------

        if len(full_text) <= chunk_size:

            chunks.append({
                "chunk_index": len(
                    chunks
                ),
                "block_index": block_index,
                "block_type": "text",
                "heading": heading,
                "text": full_text
            })

            continue

        # --------------------------------------------------
        # Split oversized text blocks
        # --------------------------------------------------

        parts = re.split(
            r"\n(?=\S)",
            content
        )

        current = heading_prefix.strip()

        for part in parts:

            part = part.strip()

            if not part:
                continue

            candidate = (
                current
                + "\n"
                + part
            ).strip()

            if len(candidate) <= chunk_size:

                current = candidate

            else:

                if current:

                    chunks.append({
                        "chunk_index": len(
                            chunks
                        ),
                        "block_index": block_index,
                        "block_type": "text",
                        "heading": heading,
                        "text": current
                    })

                # ------------------------------------------
                # Oversized individual text line
                # ------------------------------------------

                if len(part) > chunk_size:

                    start = 0

                    while start < len(
                        part
                    ):

                        end = min(
                            start + chunk_size,
                            len(part)
                        )

                        piece = part[
                            start:end
                        ].strip()

                        if piece:

                            chunks.append({
                                "chunk_index": len(
                                    chunks
                                ),
                                "block_index": block_index,
                                "block_type": "text",
                                "heading": heading,
                                "text": (
                                    heading_prefix.strip()
                                    + "\n\n"
                                    + piece
                                ).strip()
                            })

                        if end >= len(
                            part
                        ):
                            break

                        start = max(
                            end - overlap,
                            start + 1
                        )

                    current = ""

                else:

                    current = (
                        heading_prefix.strip()
                        + "\n\n"
                        + part
                    ).strip()

        if current:

            chunks.append({
                "chunk_index": len(
                    chunks
                ),
                "block_index": block_index,
                "block_type": "text",
                "heading": heading,
                "text": current
            })

    return chunks