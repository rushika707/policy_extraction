import argparse
import hashlib
import json
import os
import re
from pathlib import Path

from dotenv import load_dotenv

from app.completeness_validator import validate_policy_structure
from app.document_chunker import chunk_policy_document
from app.document_processor import create_processing_plan
from app.pdf_extractor import (
    extract_pdf_structure,
    extract_pdf_text,
)
from app.evaluation_pipeline import EvaluationPipeline
from app.policy_evaluator import PolicyEvaluator
from app.policy_extractor import (
    extract_policy_chunks,
    merge_policy_fragments,
)
from app.policy_index import build_policy_index
from app.policy_query import PolicyQuery


load_dotenv()


DEFAULT_PDF_PATH = "input/policy.pdf"
DEFAULT_INPUT_PATH = "input/test_data.json"


# ============================================================
# POLICY IDENTIFICATION
# ============================================================

def create_policy_id(pdf_path):

    pdf_path = Path(pdf_path)

    stem = re.sub(
        r"[^A-Za-z0-9_-]+",
        "_",
        pdf_path.stem
    ).strip("_")

    if not stem:
        stem = "policy"

    sha256 = hashlib.sha256()

    with open(
        pdf_path,
        "rb"
    ) as file:

        for chunk in iter(
            lambda: file.read(1024 * 1024),
            b""
        ):

            sha256.update(chunk)

    content_hash = sha256.hexdigest()[:8]

    return (
        f"{stem}_{content_hash}"
    )


def get_policy_paths(pdf_path):

    policy_id = create_policy_id(
        pdf_path
    )

    output_dir = (
        Path("output")
        / policy_id
    )

    return {
        "policy_id": policy_id,
        "directory": output_dir,

        "document":
            output_dir / "document.md",

        "metadata":
            output_dir / "document_metadata.json",

        "policy":
            output_dir / "policy.json",

        "fragments":
            output_dir / "policy_fragments.json",

        "validation":
            output_dir / "validation_report.json",

        "mock_fragments":
            output_dir / "mock_policy_fragments.json",

        "mock_policy":
            output_dir / "mock_policy.json",

        "mock_validation":
            output_dir / "mock_validation_report.json",

        "index":
            output_dir / "policy.index",

        "chunks":
            output_dir / "policy_chunks.json",

        "evaluation":
            output_dir / "evaluation_results.json"
    }


# ============================================================
# FILE HELPERS
# ============================================================

def save_json(
    data,
    path
):

    path = Path(path)

    path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        path,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            data,
            file,
            indent=2,
            ensure_ascii=False
        )


def load_json(path):

    with open(
        path,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


# ============================================================
# DOCUMENT LOADING
# ============================================================

def load_document(
    pdf_path,
    paths
):

    print()
    print("=" * 60)
    print("STEP 1 — DOCUMENT LOADING")
    print("=" * 60)

    document_path = paths["document"]

    if document_path.exists():

        print(
            "Using existing Docling Markdown:"
        )

        print(
            f"  {document_path}"
        )

        document_text = document_path.read_text(
            encoding="utf-8"
        )

    else:

        print(
            "Converting PDF using Docling:"
        )

        print(
            f"  {pdf_path}"
        )

        document_text = extract_pdf_text(
            pdf_path
        )

        document_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        document_path.write_text(
            document_text,
            encoding="utf-8"
        )

    if not document_text.strip():

        raise ValueError(
            "Document extraction returned empty text."
        )

    print(
        f"Document length: {len(document_text)} characters"
    )

    return document_text


def save_document_metadata(
    pdf_path,
    document_text,
    paths
):

    metadata = {
        "policy_id": paths["policy_id"],
        "source_file": str(pdf_path),
        "document_characters": len(
            document_text
        )
    }

    save_json(
        metadata,
        paths["metadata"]
    )


# ============================================================
# PROCESSING PLAN
# ============================================================

def show_processing_plan(
    document_text
):

    print()
    print("=" * 60)
    print("STEP 2 — DOCUMENT PROCESSING PLAN")
    print("=" * 60)

    plan = create_processing_plan(
        document_text
    )

    print(
        f"Processing mode: {plan.mode}"
    )

    if plan.mode == "full":

        print(
            "Using complete document context."
        )

    else:

        print(
            "Using structured document chunks."
        )

    return plan


# ============================================================
# GROQ CHUNK EXTRACTION
# ============================================================

def extract_policy_from_chunks(
    document_text,
    paths
):

    print()
    print("=" * 60)
    print("GROQ CHUNKED POLICY EXTRACTION")
    print("=" * 60)

    chunks = chunk_policy_document(
        document_text
    )

    if not chunks:

        raise ValueError(
            "No document chunks were generated."
        )

    print(
        f"Created {len(chunks)} document chunks."
    )

    fragments = extract_policy_chunks(
        chunks
    )

    print()
    print(
        f"Created {len(fragments)} policy fragments."
    )

    if not fragments:

        raise ValueError(
            "Groq did not produce any policy fragments."
        )

    save_json(
        fragments,
        paths["fragments"]
    )

    policy = merge_policy_fragments(
        fragments
    )

    save_json(
        policy,
        paths["policy"]
    )

    print()
    print(
        "Merged policy fragments."
    )

    print(
        "Policy JSON saved to:"
    )

    print(
        f"  {paths['policy']}"
    )

    return policy, fragments


# ============================================================
# COMPLETENESS VALIDATION
# ============================================================

def validate_policy(
    document_text,
    policy,
    paths
):

    print()
    print("=" * 60)
    print("POLICY STRUCTURE VALIDATION")
    print("=" * 60)

    report = validate_policy_structure(
        document_text,
        policy
    )

    save_json(
        report,
        paths["validation"]
    )

    valid = report.get(
        "valid",
        False
    )

    print(
        f"Valid: {valid}"
    )

    if "source_characters" in report:

        print(
            "Source characters:",
            report["source_characters"]
        )

    if "json_characters" in report:

        print(
            "JSON characters:",
            report["json_characters"]
        )

    if "source_headings" in report:

        print(
            "Source headings:",
            report["source_headings"]
        )

    if "heading_coverage" in report:

        print(
            "Heading coverage:",
            report["heading_coverage"]
        )

    if "text_coverage" in report:

        print(
            "Text coverage:",
            report["text_coverage"]
        )

    issues = report.get(
        "issues",
        []
    )

    warnings = report.get(
        "warnings",
        []
    )

    if issues:

        print()
        print("Issues:")

        for issue in issues:

            print(
                f"  - {issue}"
            )

    if warnings:

        print()
        print("Warnings:")

        for warning in warnings:

            print(
                f"  - {warning}"
            )

    return report


# ============================================================
# MOCK EXTRACTION
# ============================================================

def run_mock_extraction(
    document_text,
    paths
):

    from app.mock_policy_extractor import (
        mock_extract_policy_chunks
    )

    print()
    print("=" * 60)
    print("MOCK CHUNK EXTRACTION")
    print("=" * 60)

    chunks = chunk_policy_document(
        document_text
    )

    print(
        f"Created {len(chunks)} document chunks."
    )

    fragments = mock_extract_policy_chunks(
        chunks
    )

    print(
        f"Created {len(fragments)} mock fragments."
    )

    save_json(
        fragments,
        paths["mock_fragments"]
    )

    policy = merge_policy_fragments(
        fragments
    )

    save_json(
        policy,
        paths["mock_policy"]
    )

    report = validate_policy_structure(
        document_text,
        policy
    )

    save_json(
        report,
        paths["mock_validation"]
    )

    print()
    print(
        "Mock pipeline completed."
    )

    print(
        f"Validation: {report.get('valid')}"
    )

    print()
    print("Saved:")

    print(
        f"  {paths['mock_fragments']}"
    )

    print(
        f"  {paths['mock_policy']}"
    )

    print(
        f"  {paths['mock_validation']}"
    )

    return policy


# ============================================================
# INDEX
# ============================================================

def build_index(
    document_text,
    paths
):

    print()
    print("=" * 60)
    print("POLICY SEMANTIC INDEX")
    print("=" * 60)

    retriever = build_policy_index(
        document_text,
        index_path=str(
            paths["index"]
        ),
        chunks_path=str(
            paths["chunks"]
        )
    )

    print(
        f"Indexed {len(retriever.chunks)} chunks."
    )

    print()
    print("Index saved:")

    print(
        f"  {paths['index']}"
    )

    print(
        f"  {paths['chunks']}"
    )

    return retriever


# ============================================================
# EVALUATION
# ============================================================

def evaluate_policy(
    paths,
    input_path
):

    print()
    print("=" * 60)
    print("POLICY EVALUATION")
    print("=" * 60)

    if not paths["index"].exists():

        raise FileNotFoundError(
            f"Policy index not found: {paths['index']}"
        )

    if not paths["chunks"].exists():

        raise FileNotFoundError(
            f"Policy chunks not found: {paths['chunks']}"
        )

    if not Path(input_path).exists():

        raise FileNotFoundError(
            f"Input data not found: {input_path}"
        )

    policy_query = PolicyQuery(
        index_path=str(
            paths["index"]
        ),
        chunks_path=str(
            paths["chunks"]
        )
    )

    evaluator = PolicyEvaluator()

    input_data = load_json(
        input_path
    )

    pipeline = EvaluationPipeline(
        policy_query=policy_query,
        evaluator=evaluator
    )

    result = pipeline.evaluate(
        input_data,
        top_k=15
    )

    save_json(
        result,
        paths["evaluation"]
    )

    print()
    print(
        "Evaluation completed."
    )

    print(
        "Results saved to:"
    )

    print(
        f"  {paths['evaluation']}"
    )

    return result


# ============================================================
# ARGUMENT PARSER
# ============================================================

def parse_arguments():

    parser = argparse.ArgumentParser(
        description=(
            "Dynamic Policy Extraction "
            "and Evaluation Pipeline"
        )
    )

    parser.add_argument(
        "--policy",
        default=DEFAULT_PDF_PATH,
        help="Path to policy PDF"
    )

    parser.add_argument(
        "--input",
        default=DEFAULT_INPUT_PATH,
        help="Path to evaluation input JSON"
    )

    parser.add_argument(
        "--extract",
        action="store_true",
        help="Extract policy using Groq"
    )

    parser.add_argument(
        "--mock-extract-chunks",
        action="store_true",
        help="Run extraction pipeline without Groq"
    )

    parser.add_argument(
        "--validate",
        action="store_true",
        help="Validate existing policy JSON"
    )

    parser.add_argument(
        "--build-index",
        action="store_true",
        help="Build FAISS semantic policy index"
    )

    parser.add_argument(
        "--evaluate",
        action="store_true",
        help="Evaluate input data against policy"
    )

    parser.add_argument(
        "--all",
        action="store_true",
        help=(
            "Run extraction, validation, "
            "indexing and evaluation"
        )
    )

    return parser.parse_args()


# ============================================================
# MAIN
# ============================================================

def main():

    args = parse_arguments()

    pdf_path = Path(
        args.policy
    )

    if not pdf_path.exists():

        raise FileNotFoundError(
            f"Policy PDF not found: {pdf_path}"
        )

    paths = get_policy_paths(
        pdf_path
    )

    paths["directory"].mkdir(
        parents=True,
        exist_ok=True
    )

    print()
    print("Policy PDF:")

    print(
        f"  {pdf_path}"
    )

    print()
    print("Policy ID:")

    print(
        f"  {paths['policy_id']}"
    )

    print()
    print("Policy output directory:")

    print(
        f"  {paths['directory']}"
    )

    # --------------------------------------------------------
    # DOCUMENT
    # --------------------------------------------------------

    document_text = load_document(
        pdf_path,
        paths
    )

    save_document_metadata(
        pdf_path,
        document_text,
        paths
    )

    show_processing_plan(
        document_text
    )

    # --------------------------------------------------------
    # MOCK EXTRACTION
    # --------------------------------------------------------

    if args.mock_extract_chunks:

        run_mock_extraction(
            document_text,
            paths
        )

        return

    # --------------------------------------------------------
    # GROQ EXTRACTION
    # --------------------------------------------------------

    if args.extract or args.all:

        policy, fragments = (
            extract_policy_from_chunks(
                document_text,
                paths
            )
        )

        validate_policy(
            document_text,
            policy,
            paths
        )

    # --------------------------------------------------------
    # VALIDATION
    # --------------------------------------------------------

    if args.validate:

        if not paths["policy"].exists():

            raise FileNotFoundError(
                f"Policy JSON not found: {paths['policy']}"
            )

        policy = load_json(
            paths["policy"]
        )

        validate_policy(
            document_text,
            policy,
            paths
        )

    # --------------------------------------------------------
    # INDEX
    # --------------------------------------------------------

    if args.build_index or args.all:

        build_index(
            document_text,
            paths
        )

    # --------------------------------------------------------
    # EVALUATION
    # --------------------------------------------------------

    if args.evaluate or args.all:

        evaluate_policy(
            paths,
            args.input
        )

    # --------------------------------------------------------
    # NOTHING SELECTED
    # --------------------------------------------------------

    if not any([
        args.extract,
        args.mock_extract_chunks,
        args.validate,
        args.build_index,
        args.evaluate,
        args.all
    ]):

        print()
        print(
            "No operation selected."
        )

        print()
        print("Examples:")

        print(
            "  python run.py --policy "
            "input\\policy.pdf --extract"
        )

        print(
            "  python run.py --policy "
            "input\\policy.pdf --build-index"
        )

        print(
            "  python run.py --policy "
            "input\\policy.pdf --evaluate"
        )


if __name__ == "__main__":
    main()