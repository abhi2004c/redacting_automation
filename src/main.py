from pathlib import Path

from fake_name_maker import Anonymizer
from document_processor import redact_docx


BASE_DIR = Path(__file__).resolve().parent.parent


INPUT_FILE = (
    BASE_DIR
    / "input"
    / "Red Herring Prospectus.docx"
)


OUTPUT_FILE = (
    BASE_DIR
    / "output"
    / "redacted_prospectus.docx"
)


MAP_FILE = (
    BASE_DIR
    / "output"
    / "replacements.json"
)


def main():

    print(
        "Starting PII redaction..."
    )

    print()

    print(
        f"Input : {INPUT_FILE}"
    )

    print(
        f"Output: {OUTPUT_FILE}"
    )

    print(
        f"Map   : {MAP_FILE}"
    )

    print()

    # ---------------------------------------------------------
    # Verify input
    # ---------------------------------------------------------

    if not INPUT_FILE.exists():

        print(
            "ERROR: Input document not found."
        )

        print(
            f"Expected: {INPUT_FILE}"
        )

        return

    # ---------------------------------------------------------
    # Create anonymizer
    #
    # Existing replacements.json is loaded here.
    # ---------------------------------------------------------

    anonymizer = Anonymizer(
        MAP_FILE
    )

    # ---------------------------------------------------------
    # Process document
    # ---------------------------------------------------------

    redact_docx(
        INPUT_FILE,
        OUTPUT_FILE,
        anonymizer
    )

    # ---------------------------------------------------------
    # Save mapping
    #
    # This happens once after the entire document
    # has been processed.
    # ---------------------------------------------------------

    anonymizer.save_map()

    print()

    print(
        "PII redaction completed."
    )

    print()

    print(
        f"Redacted document:"
    )

    print(
        OUTPUT_FILE
    )

    print()

    print(
        "Replacement map:"
    )

    print(
        MAP_FILE
    )


if __name__ == "__main__":
    main()