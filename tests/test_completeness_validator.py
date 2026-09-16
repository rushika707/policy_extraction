from app.completeness_validator import (
    validate_policy_structure
)


def test_valid_dynamic_object():

    source = """
# Policy Document

## Purpose

This policy defines requirements.

## Requirements

Records must be reviewed before use.
"""

    extracted = {
        "policyMetadata": {
            "name": "Policy Document"
        },
        "sections": [
            {
                "title": "Purpose",
                "content": (
                    "This policy defines requirements."
                )
            },
            {
                "title": "Requirements",
                "content": (
                    "Records must be reviewed before use."
                )
            }
        ]
    }

    result = validate_policy_structure(
        source,
        extracted
    )

    assert result["valid"] is True


def test_valid_dynamic_list():

    source = """
# Example Policy

## Section A

First requirement.

## Section B

Second requirement.
"""

    extracted = [
        {
            "title": "Section A",
            "content": "First requirement."
        },
        {
            "title": "Section B",
            "content": "Second requirement."
        }
    ]

    result = validate_policy_structure(
        source,
        extracted
    )

    assert result["valid"] is True


def test_empty_extraction_fails():

    source = """
# Example Policy

## Requirements

Records must be reviewed.
"""

    extracted = {}

    result = validate_policy_structure(
        source,
        extracted
    )

    assert result["valid"] is False


def test_low_coverage_fails():

    source = """
# Example Policy

## Purpose

This policy contains many important
requirements that must be preserved.

## Requirements

Every record must be reviewed before use.

## Exceptions

Approved exceptions must be documented.

## Responsibilities

The responsible team must maintain evidence.
"""

    extracted = {
        "title": "Example Policy"
    }

    result = validate_policy_structure(
        source,
        extracted
    )

    assert result["valid"] is False


def test_does_not_assume_policy_domain():

    source = """
# Engineering Standard

## Materials

Material X is permitted.

## Process

The process must be completed before release.
"""

    extracted = {
        "document": {
            "title": "Engineering Standard",
            "sections": [
                {
                    "name": "Materials",
                    "text": "Material X is permitted."
                },
                {
                    "name": "Process",
                    "text": (
                        "The process must be completed "
                        "before release."
                    )
                }
            ]
        }
    }

    result = validate_policy_structure(
        source,
        extracted
    )

    assert result["valid"] is True


def test_detects_suspicious_colon_values():

    source = """
# Example Policy

## Section

Some policy information.
"""

    extracted = [
        "id",
        ":",
        "1",
        "title",
        ":",
        "Section"
    ]

    result = validate_policy_structure(
        source,
        extracted
    )

    assert result["valid"] is False

    assert len(
        result["issues"]
    ) > 0