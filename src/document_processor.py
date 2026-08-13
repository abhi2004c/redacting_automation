from docx import Document

from detector import detect_regex_pii
from name_detector import detect_ner_pii
from person_name_detector import (
    detect_context_persons,
)


def remove_overlaps(findings):

    confidence_order = {
        "HIGH": 0,
        "MEDIUM": 1,
        "LOW": 2,
    }

    # Higher-confidence detections first.
    findings.sort(
        key=lambda item: (
            item["start"],
            confidence_order.get(
                item.get("confidence"),
                99
            ),
            -(item["end"] - item["start"])
        )
    )

    result = []

    occupied_until = -1

    for finding in findings:

        if finding["start"] >= occupied_until:

            result.append(finding)

            occupied_until = finding["end"]

    return result


def process_text(text, anonymizer):

    if not text.strip():
        return text

    findings = []

    # ---------------------------------------------------------
    # 1. Regex / structured PII
    # ---------------------------------------------------------

    findings.extend(
        detect_regex_pii(text)
    )

    # ---------------------------------------------------------
    # 2. spaCy NER
    # ---------------------------------------------------------

    findings.extend(
        detect_ner_pii(text)
    )

    # ---------------------------------------------------------
    # 3. Context-based PERSON detection
    # ---------------------------------------------------------

    findings.extend(
        detect_context_persons(text)
    )

    # ---------------------------------------------------------
    # Remove already-generated fake values
    # ---------------------------------------------------------

    findings = [
        finding
        for finding in findings
        if finding["value"]
        not in anonymizer.generated_values
    ]

    # ---------------------------------------------------------
    # Remove overlapping detections
    # ---------------------------------------------------------

    findings = remove_overlaps(
        findings
    )

    # ---------------------------------------------------------
    # Replace from RIGHT to LEFT
    #
    # This is important because replacing text from
    # left to right changes character positions.
    # ---------------------------------------------------------

    findings.sort(
        key=lambda item: item["start"],
        reverse=True
    )

    result = text

    for finding in findings:

        original = finding["value"]

        replacement = anonymizer.get_replacement(
            finding["type"],
            original
        )

        result = (
            result[:finding["start"]]
            + replacement
            + result[finding["end"]:]
        )

    return result


def redact_docx(
    input_path,
    output_path,
    anonymizer
):

    document = Document(input_path)

    # ---------------------------------------------------------
    # Normal paragraphs
    # ---------------------------------------------------------

    for paragraph in document.paragraphs:

        paragraph.text = process_text(
            paragraph.text,
            anonymizer
        )

    # ---------------------------------------------------------
    # Tables
    # ---------------------------------------------------------

    for table in document.tables:

        for row in table.rows:

            for cell in row.cells:

                cell.text = process_text(
                    cell.text,
                    anonymizer
                )

    document.save(
        output_path
    )